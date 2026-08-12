from typing import override

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QPushButton

from scfile.app.gui.styles import Colors


class ProgressButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._text = text
        self._completed = 0
        self._total = 0
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self, total: int = 0) -> None:
        self._completed = 0
        self._total = total
        self._running = True
        self.setText(f"0/{total}" if total else "…")
        self.update()

    def advance(self) -> None:
        self._completed += 1
        self.setText(f"{self._completed}/{self._total}")
        self.update()

    def finish(self) -> None:
        self._completed = 0
        self._total = 0
        self._running = False
        self.setText(self._text)
        self.update()

    @override
    def paintEvent(self, event) -> None:
        if not self.running:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 4, 4)

        painter.fillPath(path, Colors.CARD.value.lighter(150))
        progress = rect.width() * self._completed / self._total if self._total else 0
        painter.save()
        painter.setClipPath(path)
        painter.fillRect(0, 0, int(progress), rect.height(), Colors.ACCENT.value)
        painter.restore()

        painter.setPen(Colors.TEXT.value)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.save()
        painter.setClipPath(path)
        painter.setClipRect(0, 0, int(progress), rect.height())
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.restore()
        painter.end()
