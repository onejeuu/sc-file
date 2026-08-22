from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.app.gui import strings
from scfile.app.gui.styles import Styles
from scfile.enums import OnConflict


class ConflictWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(strings.get("label.convert.onconflict"))
        label.setStyleSheet(Styles.LABEL)

        toggle_group = QWidget()
        toggle_layout = QHBoxLayout(toggle_group)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)

        self.buttons = QButtonGroup(self)
        self.buttons.setExclusive(True)

        for option in OnConflict:
            button = QPushButton(strings.get(f"option.convert.onconflict.{option.value}"))
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setProperty("conflict_option", option.value)
            button.setStyleSheet(Styles.TOGGLE_ITEM)
            self.buttons.addButton(button)
            toggle_layout.addWidget(button)

        self.buttons.buttons()[0].setChecked(True)
        toggle_group.setStyleSheet(Styles.TOGGLE_GROUP)

        hint = QLabel(strings.get("label.convert.onconflict.hint"))
        hint.setStyleSheet(Styles.HINT)

        layout.addWidget(label)
        layout.addWidget(toggle_group)
        layout.addWidget(hint)

    @property
    def value(self) -> OnConflict:
        button = self.buttons.checkedButton()
        value = button.property("conflict_option") if button else OnConflict.REPLACE
        return OnConflict(value)
