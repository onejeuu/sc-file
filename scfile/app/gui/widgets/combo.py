from typing import override

from PySide6.QtCore import QEvent, QObject, QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QPainterPath, QPalette, QRegion, QTextCharFormat, QTextLayout
from PySide6.QtWidgets import QApplication, QComboBox, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QWidget

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
        self._prepare_popup()

        palette = popup.palette()
        palette.setColor(QPalette.ColorRole.Base, Colors.SURFACE_RAISED.value)
        palette.setColor(QPalette.ColorRole.Text, Colors.TEXT.value)
        palette.setColor(QPalette.ColorRole.Highlight, Colors.CONTROL_HOVER.value)
        palette.setColor(QPalette.ColorRole.HighlightedText, Colors.TEXT.value)
        popup.setPalette(palette)

        self.setStyleSheet(Styles.COMBO)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _prepare_popup(self) -> None:
        container = self.view().window()
        container.setObjectName("comboPopup")
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        container.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        container.setAutoFillBackground(False)
        palette = container.palette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.transparent)
        container.setPalette(palette)
        container.setStyleSheet(Styles.COMBO_CONTAINER)
        if not container.property("roundedPopup"):
            container.setProperty("roundedPopup", True)
            container.installEventFilter(self)
        self._mask_popup(container)

    def _mask_popup(self, container: QWidget | None = None) -> None:
        widget = container or self.view().window()
        if widget.width() <= 0 or widget.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(widget.rect()), 6, 6)
        widget.setMask(QRegion(path.toFillPolygon().toPolygon()))

    @override
    def showPopup(self) -> None:
        self._prepare_popup()
        super().showPopup()
        self._prepare_popup()
        QTimer.singleShot(0, self._prepare_popup)

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.view().window() and event.type() in (QEvent.Type.Show, QEvent.Type.Resize):
            QTimer.singleShot(0, self._prepare_popup)
        return super().eventFilter(watched, event)
