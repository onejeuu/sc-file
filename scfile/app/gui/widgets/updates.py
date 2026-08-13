import time
from typing import override

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile import __version__ as SEMVER
from scfile.app import updates
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

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(Styles.POPUP)

        self.main_layout = QVBoxLayout(self)
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

        label = QLabel(strings.get("update.checking"))
        self.main_layout.addWidget(label)
        self.adjustSize()
        self.show()

    def show_status(self, status: UpdateStatus, message: str, url: str):
        self._clear_state()

        match status:
            case UpdateStatus.UPTODATE:
                label = QLabel(strings.get("update.uptodate"))
                label.setStyleSheet(f"color: {Colors.SUCCESS};")
                self.main_layout.addWidget(label)
                self.close_timer.start(3000)

            case UpdateStatus.AVAILABLE:
                label = QLabel(strings.get("update.available"))
                label.setStyleSheet(f"color: {Colors.INFO};")
                self.main_layout.addWidget(label)
                self.main_layout.addWidget(LinkWidget(text=url, url=url))

            case UpdateStatus.ERROR:
                label = QLabel(f"{strings.get('update.error')}: {message}")
                label.setStyleSheet(f"color: {Colors.ERROR};")
                self.main_layout.addWidget(label)

                if url:
                    warn = QLabel(strings.get("update.manual"))
                    warn.setStyleSheet(f"color: {Colors.WARNING};")
                    self.main_layout.addWidget(warn)
                    self.main_layout.addWidget(LinkWidget(text=url, url=url))

        self.adjustSize()
        self.show()

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_position()

    def update_position(self):
        anchor = self.anchor.rect()
        position = self.anchor.mapToGlobal(anchor.topLeft())

        x = position.x()
        y = position.y() - self.height() - 4
        self.move(x, y)


class VersionWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(Styles.LINK)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        v = Version.parse(SEMVER)
        tag = v.tag if v else SEMVER

        self.text_label = QLabel(tag)
        self.main_layout.addWidget(self.text_label)

        self.popup: UpdatePopup | None = None
        self.checker = UpdateChecker(parent=self)
        self.checker.status.connect(self._status)

    def leaveEvent(self, event):
        self.setStyleSheet(Styles.LINK)
        super().leaveEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet(Styles.LINK_HOVER)
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
