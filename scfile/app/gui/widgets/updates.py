import time
from typing import override

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile import __version__ as SEMVER
from scfile.app import files, updates
from scfile.app.enums import UpdateStatus
from scfile.app.gui import strings, threads
from scfile.app.gui.styles import Colors, Styles
from scfile.app.updates import UpdateCheck
from scfile.app.version import Version

from .link import LinkWidget


class UpdatesWorker(threads.JobWorker):
    status = Signal(UpdateStatus, str, str)

    def _run(self) -> None:
        try:
            self.status.emit(*updates.check(SEMVER))

        except Exception as error:
            self.status.emit(UpdateStatus.ERROR, str(error), "")


class UpdateChecker(QObject):
    status = Signal(UpdateStatus, str, str)

    def __init__(self, ttl: int = 60, parent: QObject | None = None):
        super().__init__(parent)
        self._ttl = ttl
        self._cached: UpdateCheck | None = None
        self._cached_at = 0.0
        self._worker: UpdatesWorker | None = None
        self._thread: QThread | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def start(self) -> bool:
        if self._cached is not None and time.time() - self._cached_at < self._ttl:
            self.status.emit(*self._cached)
            return False

        if self.busy:
            return False

        self._worker = UpdatesWorker()
        self._worker.status.connect(self._status)
        self._thread = threads.job(self, self._worker)
        self._thread.finished.connect(self._finished)
        self._thread.start()
        return True

    def stop(self) -> None:
        if not self.busy or self._thread is None:
            return

        threads.stop(self._thread)
        self._worker = None
        self._thread = None

    def _status(self, status: UpdateStatus, message: str, url: str) -> None:
        result = UpdateCheck(status, message, url)
        if status in (UpdateStatus.UPTODATE, UpdateStatus.AVAILABLE):
            self._cached = result
            self._cached_at = time.time()

        self.status.emit(*result)

    def _finished(self) -> None:
        self._worker = None
        self._thread = None


class UpdatePopup(QWidget):
    def __init__(self, anchor: QWidget):
        flags = Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(anchor, flags)
        self.anchor = anchor
        owner = anchor
        while owner is not None:
            owner.installEventFilter(self)
            owner = owner.parentWidget()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(Styles.UPDATE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        surface = QWidget(self)
        surface.setObjectName("updateSurface")
        surface.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        layout.addWidget(surface)

        self.main_layout = QVBoxLayout(surface)
        self.main_layout.setContentsMargins(10, 8, 10, 8)
        self.main_layout.setSpacing(6)

        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.close)

    def _clear_state(self):
        self.close_timer.stop()

        while self.main_layout.count():
            if item := self.main_layout.takeAt(0):
                if w := item.widget():
                    w.setParent(None)
                    w.deleteLater()

    def show_loading(self):
        self._clear_state()

        self._message(strings.get("update.checking"), "updates.checking", Colors.INFO)
        self.adjustSize()
        self.show()

    def _message(self, text: str, icon: str, color: Colors) -> QLabel:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        pixmap = QPixmap(str(files.resource(f"assets/{icon}.png"))).scaled(
            QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color.value)
        painter.end()

        image = QLabel()
        image.setPixmap(pixmap)
        layout.addWidget(image)

        label = QLabel(text)
        label.setStyleSheet(f"color: {color};")
        layout.addWidget(label, 1)
        self.main_layout.addWidget(row)
        return label

    def show_status(self, status: UpdateStatus, message: str, url: str):
        self._clear_state()

        match status:
            case UpdateStatus.UPTODATE:
                self._message(strings.get("update.uptodate"), "updates.uptodate", Colors.SUCCESS)
                self.close_timer.start(3000)

            case UpdateStatus.AVAILABLE:
                self._message(strings.get("update.available"), "updates.available", Colors.INFO)
                if url:
                    self.main_layout.addWidget(LinkWidget(text=url, url=url))

            case UpdateStatus.ERROR:
                label = self._message(strings.get("update.error"), "widget.warning", Colors.WARNING)
                label.setToolTip(message)

                if url:
                    self.main_layout.addWidget(LinkWidget(text=url, url=url))

        self.adjustSize()
        self.show()

    @override
    def eventFilter(self, watched, event):
        if self.isVisible():
            if event.type() in (QEvent.Type.Move, QEvent.Type.Resize):
                self.update_position()
            elif event.type() == QEvent.Type.Hide:
                self.close()
        return super().eventFilter(watched, event)

    @override
    def showEvent(self, event):
        super().showEvent(event)
        self.update_position()

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_position()

    def update_position(self):
        anchor = self.anchor.rect()
        position = self.anchor.mapToGlobal(anchor.topLeft())

        x = position.x()
        y = position.y() - self.height() - 4
        screen = self.anchor.screen().availableGeometry()
        if y < screen.top():
            y = position.y() + anchor.height() + 4
        x = max(screen.left(), min(x, screen.right() - self.width() + 1))
        y = max(screen.top(), min(y, screen.bottom() - self.height() + 1))
        self.move(x, y)


class VersionWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("versionBadge")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(Styles.VERSION_BADGE)
        self.setToolTip(strings.get("update.check"))

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(3, 0, 3, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        v = Version.parse(SEMVER)
        tag = v.tag if v else SEMVER

        self.text_label = QLabel(tag)
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.main_layout.addWidget(self.text_label)

        self.popup: UpdatePopup | None = None
        self.checker = UpdateChecker(parent=self)
        self.checker.status.connect(self._status)

    def leaveEvent(self, event):
        self.setStyleSheet(Styles.VERSION_BADGE)
        super().leaveEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet(Styles.VERSION_BADGE_HOVER)
        super().enterEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            self.start_update()
        super().mouseReleaseEvent(event)

    def start_update(self):
        if not self.popup:
            self.popup = UpdatePopup(self)

        if self.checker.start():
            self.popup.show_loading()

    def stop(self) -> None:
        self.checker.stop()

    def _status(self, status: UpdateStatus, message: str, url: str) -> None:
        if self.popup:
            self.popup.show_status(status, message, url)
