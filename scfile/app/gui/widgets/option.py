from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from scfile.app.gui.styles import Styles


class OptionWidget(QWidget):
    changed = Signal(bool)

    def __init__(self, text: str, hint: str | None = None, checked: bool = False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.checkbox = QCheckBox(text)
        self.checkbox.setStyleSheet(Styles.CHECKBOX)
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(checked)
        self.checkbox.toggled.connect(self.changed.emit)

        layout.addWidget(self.checkbox)

        if hint:
            label = QLabel(hint)
            label.setStyleSheet(Styles.HINT)
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(label)

    @property
    def checked(self) -> bool:
        return self.checkbox.isChecked()

    @checked.setter
    def checked(self, state: bool) -> None:
        self.checkbox.setChecked(state)
