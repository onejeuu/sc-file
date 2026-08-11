from collections.abc import Iterable

from PySide6.QtWidgets import QLabel

from scfile.app.gui.styles import Styles


class WarningsWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(Styles.WARNING)
        self.setWordWrap(True)
        self.hide()

    def set_messages(self, warnings: Iterable[str]) -> None:
        warnings = tuple(warnings)
        if not warnings:
            self.hide()
            return

        self.setText("\n".join(f"⚠️ {warning}" for warning in warnings))
        self.show()
