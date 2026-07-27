from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.core.options import ON_CONFLICT_OPTIONS, OnConflict
from scfile.gui.shared import strings
from scfile.gui.shared.styles import Styles


class ConflictWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(strings.get("label.onconflict"))
        label.setStyleSheet(Styles.LABEL)

        toggle_group = QWidget()
        toggle_layout = QHBoxLayout(toggle_group)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)

        self.buttons = QButtonGroup(self)
        self.buttons.setExclusive(True)

        for option in ON_CONFLICT_OPTIONS:
            button = QPushButton(strings.get(f"option.onconflict.{option}"))
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setProperty("conflict_option", option)
            button.setStyleSheet(Styles.TOGGLE_ITEM)
            self.buttons.addButton(button)
            toggle_layout.addWidget(button)

        self.buttons.buttons()[0].setChecked(True)
        toggle_group.setStyleSheet(Styles.TOGGLE_GROUP)

        hint = QLabel(strings.get("hint.onconflict"))
        hint.setStyleSheet(Styles.HINT)

        layout.addWidget(label)
        layout.addWidget(toggle_group)
        layout.addWidget(hint)

    def value(self) -> OnConflict:
        button = self.buttons.checkedButton()
        return cast(OnConflict, button.property("conflict_option") if button else "overwrite")
