from collections.abc import Iterable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from scfile.app import files
from scfile.app.gui.styles import Colors, Styles


class WarningsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        source = QPixmap(str(files.resource("assets/widget.warning.png"))).scaled(
            QSize(16, 16),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        icon = QPixmap(source.size())
        icon.fill(Qt.GlobalColor.transparent)
        painter = QPainter(icon)
        painter.drawPixmap(0, 0, source)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(icon.rect(), Colors.WARNING.value)
        painter.end()

        image = QLabel()
        image.setPixmap(icon)
        layout.addWidget(image, 0, Qt.AlignmentFlag.AlignTop)

        self.message = QLabel()
        self.message.setStyleSheet(Styles.WARNING)
        self.message.setWordWrap(True)
        layout.addWidget(self.message, 1)
        self.hide()

    def set_messages(self, warnings: Iterable[str]) -> None:
        warnings = tuple(warnings)
        if not warnings:
            self.hide()
            return

        self.message.setText("\n".join(warnings))
        self.show()
