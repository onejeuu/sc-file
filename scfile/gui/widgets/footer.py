from typing import Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QMouseEvent, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from scfile import __version__
from scfile.gui.shared import utils
from scfile.gui.shared.styles import Colors, Styles


class LinkLabel(QWidget):
    def __init__(self, text: str, url: str, icon: Optional[str] = None, parent: Optional[QWidget] = None):
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
            pixmap = QPixmap(str(utils.get_resource(icon)))
            pixmap = pixmap.scaled(12, 12, aspect, mode)
            self.icon_label.setPixmap(pixmap)
            layout.addWidget(self.icon_label)

        self.text_label = QLabel(text)
        layout.addWidget(self.text_label)

    def enterEvent(self, event):
        self.setStyleSheet(f"color: {Colors.ACCENT};")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(Styles.LINK)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.rect().contains(event.pos()):
                QDesktopServices.openUrl(QUrl(self.url))
        super().mouseReleaseEvent(event)


class FooterWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 5)
        layout.setSpacing(10)

        version = __version__

        links = [
            LinkLabel(text=f"v{version}", url=f"https://github.com/onejeuu/sc-file/releases/tag/v{version}"),
            LinkLabel(text="onejeuu/sc-file", url="https://github.com/onejeuu/sc-file"),
        ]

        for link in links:
            layout.addWidget(link)

        layout.addStretch()
