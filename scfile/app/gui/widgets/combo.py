from typing import override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate

from scfile.app.gui.styles import Colors, Styles


class ComboItemDelegate(QStyledItemDelegate):
    @override
    def sizeHint(self, option, index) -> QSize:
        size = super().sizeHint(option, index)
        size.setHeight(28)
        return size


class ComboBox(QComboBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setItemDelegate(ComboItemDelegate(self))
        popup = self.view()
        popup.setStyleSheet(Styles.COMBO_POPUP)
        popup.setMouseTracking(True)
        popup.viewport().setMouseTracking(True)

        palette = popup.palette()
        palette.setColor(QPalette.ColorRole.Base, Colors.SURFACE_RAISED.value)
        palette.setColor(QPalette.ColorRole.Text, Colors.TEXT.value)
        palette.setColor(QPalette.ColorRole.Highlight, Colors.CONTROL_HOVER.value)
        palette.setColor(QPalette.ColorRole.HighlightedText, Colors.TEXT.value)
        popup.setPalette(palette)

        self.setStyleSheet(Styles.COMBO)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
