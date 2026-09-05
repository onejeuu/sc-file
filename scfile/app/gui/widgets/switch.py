from typing import override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QAbstractButton, QWidget

from scfile.app.gui.styles import Colors


class Switch(QAbstractButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(self.sizeHint())

    @override
    def sizeHint(self) -> QSize:
        return QSize(38, 22)

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        hovered = self.underMouse() or bool(self.property("hovered"))
        if not self.isEnabled():
            track = Colors.DISABLED.value
            thumb = Colors.TEXT_DISABLED.value
        elif self.isChecked():
            track = Colors.ACCENT_HOVER.value if hovered else Colors.ACCENT.value
            thumb = Colors.ACCENT_FOREGROUND.value
        else:
            track = Colors.BORDER_STRONG.value if hovered else Colors.CONTROL_PRESSED.value
            thumb = Colors.TEXT_SECONDARY.value

        track_rect = self.rect().adjusted(1, 2, -1, -2)
        painter.setBrush(track)
        painter.drawRoundedRect(track_rect, 9, 9)

        diameter = 14
        x = self.width() - diameter - 4 if self.isChecked() else 4
        painter.setBrush(thumb)
        painter.drawEllipse(x, 4, diameter, diameter)
