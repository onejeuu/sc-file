from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app.gui.styles import Styles


class OptionWidget(QWidget):
    changed = Signal(bool)

    def __init__(
        self,
        text: str,
        hint: str | None = None,
        checked: bool = False,
        icon: QIcon | None = None,
    ):
        super().__init__()
        self._icon = icon is not None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(Styles.CHECKBOX)
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(checked)
        self.checkbox.toggled.connect(self.changed.emit)

        if icon is None:
            self.checkbox.setText(text)
            layout.addWidget(self.checkbox)

            if hint:
                label = QLabel(hint)
                label.setStyleSheet(Styles.HINT)
                label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                layout.addWidget(label)
            return

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        image = QLabel()
        image.setPixmap(icon.pixmap(QSize(20, 20)))
        image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        row.addWidget(image)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(2)
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold;")
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content.addWidget(label)
        if hint:
            description = QLabel(hint)
            description.setStyleSheet(Styles.HINT)
            description.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            content.addWidget(description)

        row.addLayout(content)
        row.addStretch()
        row.addWidget(self.checkbox)
        layout.addLayout(row)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._icon and event.button() is Qt.MouseButton.LeftButton:
            self.checkbox.toggle()
            event.accept()
            return

        super().mousePressEvent(event)

    @property
    def checked(self) -> bool:
        return self.checkbox.isChecked()

    @checked.setter
    def checked(self, state: bool) -> None:
        self.checkbox.setChecked(state)
