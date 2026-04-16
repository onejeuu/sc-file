from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from scfile.gui.shared.styles import Styles


class OptionWidget(QWidget):
    changed = Signal(bool)

    def __init__(self, text: str, hint: str | None = None, checked: bool = False):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)

        self.checkbox = QCheckBox(text)
        self.checkbox.setStyleSheet(Styles.CHECKBOX)
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(checked)
        self.checkbox.toggled.connect(self.changed.emit)

        self.main_layout.addWidget(self.checkbox)

        if hint:
            self.hint_label = QLabel(hint)
            self.hint_label.setStyleSheet(Styles.HINT)
            self.hint_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.main_layout.addWidget(self.hint_label)

    def isChecked(self) -> bool:
        return self.checkbox.isChecked()

    def setChecked(self, state: bool):
        self.checkbox.setChecked(state)
