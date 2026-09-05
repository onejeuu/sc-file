from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from scfile.app.gui.styles import Styles


class CardWidget(QWidget):
    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(Styles.CARD)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        if title:
            label = QLabel(title)
            label.setStyleSheet(Styles.CARD_TITLE)
            layout.addWidget(label)

        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(4)
        layout.addLayout(self.content)


class CalloutWidget(CardWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setObjectName("callout")
        self.setStyleSheet(Styles.CALLOUT)
