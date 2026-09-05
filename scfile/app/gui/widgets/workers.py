from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QSpinBox


class WorkersSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setRange(1, 99)
        self.setKeyboardTracking(False)

    def validate(self, text: str, pos: int):
        if not text:
            return QValidator.State.Intermediate, text, pos
        state = QValidator.State.Acceptable if text.isascii() and text.isdecimal() else QValidator.State.Invalid
        return state, text, pos

    def valueFromText(self, text: str) -> int:
        return max(1, min(99, int(text))) if text else 1
