import os
from collections.abc import Iterable
from pathlib import Path
from typing import override

from PySide6.QtCore import QMimeData, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDragMoveEvent,
    QDropEvent,
    QFont,
    QGuiApplication,
    QIcon,
    QKeyEvent,
    QKeySequence,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QMenu

from scfile import types
from scfile.app import files
from scfile.app.gui import strings
from scfile.app.gui.styles import Colors, Styles


def _source_name(source: types.SourceLike) -> str:
    path = Path(source)
    return path.name or path.anchor.rstrip("/\\")


def _source_key(source: types.SourceLike) -> str:
    return os.path.normcase(str(Path(source).resolve()))


class SourcesWidget(QListWidget):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._drag_over = False

        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet(Styles.SOURCES_EMPTY)
        self.setMinimumWidth(320)
        self.setIconSize(QSize(16, 16))

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Highlight, Colors.CONTROL_HOVER.value)
        palette.setColor(QPalette.ColorRole.HighlightedText, Colors.TEXT.value)
        self.setPalette(palette)

        self._file_icon = self._prepare_source_icon("assets/source.file.png")
        self._folder_icon = self._prepare_source_icon("assets/source.folder.png")
        self._placeholder_icon = self._prepare_placeholder_icon()
        self._placeholder_title = strings.get("convert.sources.title")
        self._placeholder_description = strings.get("convert.sources.description")

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(str(self.item(index).data(Qt.ItemDataRole.UserRole)) for index in range(self.count()))

    def add_sources(self, sources: Iterable[types.SourceLike]) -> None:
        existing = {_source_key(source) for source in self.values}

        for source in sources:
            if not source:
                continue

            value = str(source)
            key = _source_key(value)
            if key in existing:
                continue

            item = QListWidgetItem(_source_name(source))
            item.setData(Qt.ItemDataRole.UserRole, value)
            item.setToolTip(str(Path(source).resolve()))
            item.setIcon(self._folder_icon if Path(source).is_dir() else self._file_icon)
            self.addItem(item)
            existing.add(key)

        self._sync_visual_state()
        self.changed.emit()

    def _remove_selected(self) -> None:
        for item in reversed(self.selectedItems()):
            self.takeItem(self.row(item))

        self._sync_visual_state()
        self.changed.emit()

    def _sync_visual_state(self) -> None:
        style = Styles.SOURCES_EMPTY if self.count() == 0 else Styles.SOURCES_LIST
        if self.styleSheet() != style:
            self.setStyleSheet(style)
        self.viewport().update()

    def _add_mime(self, data: QMimeData) -> bool:
        if data.hasUrls():
            if sources := [url.toLocalFile() for url in data.urls() if url.isLocalFile()]:
                QTimer.singleShot(0, lambda: self.add_sources(sources))
                return True
        return False

    def _paste_from_clipboard(self) -> None:
        self._add_mime(QGuiApplication.clipboard().mimeData())

    def contextMenuEvent(self, event) -> None:
        if not self.itemAt(event.pos()):
            return

        menu = QMenu(self)
        menu.setStyleSheet(Styles.MENU)
        remove_action = QAction(strings.get("button.convert.remove.source"), self)
        remove_action.triggered.connect(self._remove_selected)
        menu.addAction(remove_action)
        menu.exec(event.globalPos())

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self._remove_selected()
            event.accept()
            return

        if event.matches(QKeySequence.StandardKey.Paste):
            self._paste_from_clipboard()
            event.accept()
            return

        super().keyPressEvent(event)

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            self._set_drag_over(True)
            event.acceptProposedAction()

    @override
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    @override
    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._set_drag_over(False)
        super().dragLeaveEvent(event)

    @override
    def dropEvent(self, event: QDropEvent) -> None:
        self._set_drag_over(False)
        if self._add_mime(event.mimeData()):
            event.acceptProposedAction()

    def _set_drag_over(self, value: bool) -> None:
        if self._drag_over == value:
            return
        self._drag_over = value
        self.viewport().update()

    def _prepare_placeholder_icon(self) -> QPixmap:
        raw = QPixmap(str(files.resource("assets/empty.sources.png")))
        return self._tint_icon(raw, Colors.TEXT_MUTED.value).scaled(
            200,
            200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _prepare_source_icon(self, resource: str) -> QIcon:
        raw = QPixmap(str(files.resource(resource)))
        icon = QIcon()
        icon.addPixmap(self._tint_icon(raw, Colors.TEXT_MUTED.value), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addPixmap(self._tint_icon(raw, Colors.TEXT_SECONDARY.value), QIcon.Mode.Selected, QIcon.State.Off)
        return icon

    @staticmethod
    def _tint_icon(source: QPixmap, color: QColor) -> QPixmap:
        tinted = QPixmap(source.size())
        tinted.fill(Qt.GlobalColor.transparent)

        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, source)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), color)
        painter.end()
        return tinted

    @override
    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.count() > 0:
            if self._drag_over:
                painter.setPen(QPen(Colors.ACCENT.value, 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -2, -2), 7, 7)
            painter.end()
            return

        border = Colors.ACCENT.value if self._drag_over else Colors.BORDER.value
        painter.setPen(QPen(border, 2, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -2, -2), 7, 7)

        viewport = self.viewport().rect()
        content_width = max(0, viewport.width() - 48)
        flags = Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap

        title_font = QFont("Segoe UI Variable", 16)
        title_font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(title_font)
        title = painter.fontMetrics().boundingRect(QRect(0, 0, content_width, 0), flags, self._placeholder_title)

        description_font = QFont("Segoe UI Variable", 11)
        painter.setFont(description_font)
        description = painter.fontMetrics().boundingRect(
            QRect(0, 0, content_width, 0), flags, self._placeholder_description
        )

        icon = self._placeholder_icon
        spacing_before_title = 24
        spacing_before_description = 8
        content = QRect(
            0,
            0,
            max(icon.width(), title.width(), description.width()),
            icon.height() + spacing_before_title + title.height() + spacing_before_description + description.height(),
        )
        content.moveCenter(viewport.center())

        painter.drawPixmap(content.left() + (content.width() - icon.width()) // 2, content.top(), icon)

        title.moveTop(content.top() + icon.height() + spacing_before_title)
        title.moveLeft(content.left())
        title.setWidth(content.width())
        painter.setFont(title_font)
        painter.setPen(Colors.TEXT.value)
        painter.drawText(title, flags, self._placeholder_title)

        description.moveTop(title.bottom() + spacing_before_description)
        description.moveLeft(content.left())
        description.setWidth(content.width())
        painter.setFont(description_font)
        painter.setPen(Colors.TEXT_MUTED.value)
        painter.drawText(description, flags, self._placeholder_description)
        painter.end()
