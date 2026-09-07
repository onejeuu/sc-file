from typing import override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton


class ToggleButton(QPushButton):
    @override
    def sizeHint(self) -> QSize:
        self.ensurePolished()
        option = QStyleOptionButton()
        self.initStyleOption(option)
        font = QFont(self.font())
        font.setWeight(QFont.Weight.Bold)
        metrics = QFontMetrics(font)
        content = metrics.size(Qt.TextFlag.TextShowMnemonic, self.text()) + QSize(4, 0)
        return self.style().sizeFromContents(QStyle.ContentsType.CT_PushButton, option, content, self)

    @override
    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()
