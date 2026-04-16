from typing import Callable, Optional, TypeAlias

from PySide6.QtWidgets import QLabel

from scfile.gui.shared.styles import Styles


Validator: TypeAlias = Callable[[], Optional[str]]


class WarningsWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(Styles.WARNING)
        self.setWordWrap(True)
        self.hide()

        self._rules: list[Validator] = []

    def add_rule(self, rule: Validator):
        self._rules.append(rule)

    def update_state(self):
        active_warns = []
        for rule in self._rules:
            if error := rule():
                active_warns.append(error)

        self.display(active_warns)

    def display(self, warnings: list[str]):
        if not warnings:
            self.hide()
            return

        self.setText("\n".join([f"⚠️ {w}" for w in warnings]))
        self.show()
