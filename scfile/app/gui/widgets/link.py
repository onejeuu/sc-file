from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QMouseEvent, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QToolTip, QWidget

from scfile.app import files
from scfile.app.gui import strings
from scfile.app.gui.styles import Styles


class LinkWidget(QWidget):
    def __init__(self, text: str, url: str, icon: str | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.url = url

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(Styles.LINK)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        if icon:
            self.icon_label = QLabel()
            aspect = Qt.AspectRatioMode.KeepAspectRatio
            mode = Qt.TransformationMode.SmoothTransformation
            pixmap = QPixmap(str(files.resource(icon)))
            pixmap = pixmap.scaled(12, 12, aspect, mode)
            self.icon_label.setPixmap(pixmap)
            self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(self.icon_label)

        self.text_label = QLabel(text)
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self.text_label)

    def leaveEvent(self, event):
        self.setStyleSheet(Styles.LINK)
        super().leaveEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet(Styles.LINK_HOVER)
        super().enterEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.rect().contains(event.pos()) or not self.url:
            super().mouseReleaseEvent(event)
            return

        match event.button():
            case Qt.MouseButton.LeftButton:
                QDesktopServices.openUrl(QUrl(self.url))
                event.accept()
                return

            case Qt.MouseButton.RightButton:
                QApplication.clipboard().setText(self.url)
                QToolTip.showText(event.globalPosition().toPoint(), strings.get("tooltip.link.copied"), self)
                event.accept()
                return

        super().mouseReleaseEvent(event)
