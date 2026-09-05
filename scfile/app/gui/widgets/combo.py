from typing import override

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QPalette, QTextCharFormat, QTextLayout
from PySide6.QtWidgets import QApplication, QComboBox, QStyle, QStyledItemDelegate, QStyleOptionViewItem

from scfile.app.gui.styles import Colors, Styles

TITLE_ROLE = int(Qt.ItemDataRole.UserRole) + 1
DETAIL_ROLE = TITLE_ROLE + 1


class ComboItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index) -> None:
        detail = index.data(DETAIL_ROLE)
        if not detail:
            super().paint(painter, option, index)
            return

        item = QStyleOptionViewItem(option)
        self.initStyleOption(item, index)
        title = index.data(TITLE_ROLE)
        item.text = ""
        style = item.widget.style() if item.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, item, painter, item.widget)
        rect = option.rect.adjusted(10, 0, -10, 0)
        text = f"{title} ({detail})"
        text_layout = QTextLayout(text, item.font, painter.device())
        formats = []
        for start, length, color in (
            (0, len(title), Colors.TEXT.value),
            (len(title), len(text) - len(title), Colors.TEXT_MUTED.value),
        ):
            span = QTextLayout.FormatRange()
            span.start = start
            span.length = length
            span.format = QTextCharFormat()
            span.format.setForeground(color)
            formats.append(span)
        text_layout.setFormats(formats)
        text_layout.beginLayout()
        line = text_layout.createLine()
        line.setNumColumns(len(text))
        text_layout.endLayout()
        painter.save()
        painter.setClipRect(rect)
        text_layout.draw(painter, QPointF(rect.left(), rect.top() + (rect.height() - line.height()) / 2))
        painter.restore()

    @override
    def sizeHint(self, option, index) -> QSize:
        size = super().sizeHint(option, index)
        size.setHeight(28)
        return size


class ComboBox(QComboBox):
    def add_named_item(self, key: str, title: str | None = None) -> None:
        self.addItem(f"{title} ({key})" if title else key, key)
        if title:
            index = self.count() - 1
            self.setItemData(index, title, TITLE_ROLE)
            self.setItemData(index, key, DETAIL_ROLE)

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
