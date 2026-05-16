from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile import __version__ as SEMVER
from scfile.enums import UpdateStatus
from scfile.gui.shared.strings import Str
from scfile.gui.shared.styles import Colors, Styles
from scfile.gui.workers.updates import UpdatesWorker
from scfile.utils import versions

from .link import LinkWidget


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

    def _clear_layout(self):
        while self.main_layout.count():
            if item := self.main_layout.takeAt(0):
                if w := item.widget():
                    w.setParent(None)
                    w.deleteLater()

    def show_loading(self):
        self._clear_layout()
        label = QLabel(Str.get("update_checking"))
        self.main_layout.addWidget(label)
        self.adjustSize()
        self.show()

    def show_status(self, status: UpdateStatus, info: str, url: str):
        self._clear_layout()

        match status:
            case UpdateStatus.UPTODATE:
                label = QLabel(Str.get("update_uptodate"))
                label.setStyleSheet(f"color: {Colors.SUCCESS};")
                self.main_layout.addWidget(label)
                QTimer.singleShot(3000, self.close)

            case UpdateStatus.AVAILABLE:
                label = QLabel(Str.get("update_available"))
                label.setStyleSheet(f"color: {Colors.INFO};")
                self.main_layout.addWidget(label)
                self.main_layout.addWidget(LinkWidget(text=url, url=url))

            case UpdateStatus.ERROR:
                label = QLabel(f"{Str.get('update_error')}: {info}")
                label.setStyleSheet(f"color: {Colors.ERROR};")
                self.main_layout.addWidget(label)

                if url:
                    warn = QLabel(Str.get("update_manual"))
                    warn.setStyleSheet(f"color: {Colors.WARNING};")
                    self.main_layout.addWidget(warn)
                    self.main_layout.addWidget(LinkWidget(text=url, url=url))

        self.adjustSize()
        self.show()

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

        v = versions.parse(SEMVER)
        tag = v.tag if v else SEMVER

        self.text_label = QLabel(tag)
        self.main_layout.addWidget(self.text_label)

        self.popup: UpdatePopup | None = None
        self.worker: UpdatesWorker | None = None

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
        if self.worker and self.worker.isRunning():
            return

        if not self.popup:
            self.popup = UpdatePopup(self)

        self.popup.show_loading()

        self.worker = UpdatesWorker()
        self.worker.status.connect(self.handle_status)
        self.worker.start()

    def handle_status(self, status: UpdateStatus, info: str, url: str):
        if self.popup:
            self.popup.show_status(status, info, url)
