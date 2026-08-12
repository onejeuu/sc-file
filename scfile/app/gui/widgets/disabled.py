from typing import override

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget


class DisabledCursor(QObject):
    def __init__(self, target: QWidget):
        super().__init__(target)
        self.target = target
        self.overlay = _DisabledOverlay(target.parentWidget())
        self.overlay.setCursor(Qt.CursorShape.ForbiddenCursor)
        target.installEventFilter(self)

    def set(self, enabled: bool, tooltip: str = "") -> None:
        self.target.setEnabled(enabled)
        self.overlay.setToolTip(tooltip)
        self._sync()
        self.overlay.setVisible(not enabled)

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.target and event.type() in (QEvent.Type.Move, QEvent.Type.Resize, QEvent.Type.Show):
            self._sync()

        return super().eventFilter(watched, event)

    def _sync(self) -> None:
        self.overlay.setGeometry(self.target.geometry())
        self.overlay.raise_()


class _DisabledOverlay(QWidget):
    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        event.accept()
