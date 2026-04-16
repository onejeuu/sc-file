from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from scfile.gui.shared.styles import Styles


class RetargetTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Retarget (WIP)")
        label.setStyleSheet(Styles.TITLE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
