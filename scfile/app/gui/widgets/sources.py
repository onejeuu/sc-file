import os
from collections.abc import Iterable
from pathlib import Path
from typing import override

from PySide6.QtCore import QFileInfo, QMimeData, QRect, Qt, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QFont,
    QGuiApplication,
    QKeyEvent,
    QKeySequence,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileIconProvider,
    QListWidget,
    QListWidgetItem,
    QMenu,
)

from scfile import types
from scfile.app import files
from scfile.app.gui import strings
from scfile.app.gui.styles import Colors, Styles


_PATH_ALIASES = tuple(
    (Path(path).resolve(), alias)
    for path, alias in (
        (os.environ.get("APPDATA"), "%APPDATA%"),
        (Path.home(), "~"),
    )
    if path
)


def _display_path(source: types.SourceLike) -> str:
    path = Path(source).resolve()

    for root, alias in _PATH_ALIASES:
        if path.is_relative_to(root):
            relative = path.relative_to(root)
            return f"{alias}/{relative.as_posix()}" if relative.parts else alias

    return path.as_posix()


class SourcesWidget(QListWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.icon_provider = QFileIconProvider()

        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet(Styles.LIST)
        self.setMinimumWidth(320)

        self._placeholder_icon = self._prepare_placeholder_icon()
        self._placeholder_text = strings.get("converter.hint")

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(str(self.item(index).data(Qt.ItemDataRole.UserRole)) for index in range(self.count()))

    def add_sources(self, sources: Iterable[types.SourceLike]) -> None:
        for source in sources:
            if not source:
                continue

            label = _display_path(source)
            existing = self.findItems(label, Qt.MatchFlag.MatchExactly)
            if existing:
                continue

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, str(source))
            item.setIcon(self.icon_provider.icon(QFileInfo(str(source))))
            self.addItem(item)

        self.changed.emit()

    def _remove_selected(self):
        for item in reversed(self.selectedItems()):
            self.takeItem(self.row(item))

        self.changed.emit()

    def _add_mime(self, data: QMimeData) -> bool:
        if data.hasUrls():
            if sources := [url.toLocalFile() for url in data.urls() if url.isLocalFile()]:
                QTimer.singleShot(0, lambda: self.add_sources(sources))
                return True
        return False

    def _paste_from_clipboard(self):
        self._add_mime(QGuiApplication.clipboard().mimeData())

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            menu = QMenu(self)
            remove_action = QAction(strings.get("button.remove_source"), self)
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
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    @override
    def dropEvent(self, event: QDropEvent):
        if self._add_mime(event.mimeData()):
            event.acceptProposedAction()

    def _prepare_placeholder_icon(self) -> QPixmap:
        aspect = Qt.AspectRatioMode.KeepAspectRatio
        mode = Qt.TransformationMode.SmoothTransformation
        raw = QPixmap(str(files.resource("assets/upload.png"))).scaled(64, 64, aspect, mode)

        tinted = QPixmap(raw.size())
        tinted.fill(Qt.GlobalColor.transparent)

        paint = QPainter(tinted)
        paint.drawPixmap(0, 0, raw)
        paint.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        paint.fillRect(tinted.rect(), QColor(Colors.TEXT.dark))
        paint.end()
        return tinted

    @override
    def paintEvent(self, event):
        super().paintEvent(event)

        if self.count() > 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QColor(Colors.TEXT.dark))

        viewport = self.viewport().rect()
        icon = self._placeholder_icon
        text = self._placeholder_text
        flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
        spacing = 8

        label = painter.fontMetrics().boundingRect(QRect(0, 0, viewport.width(), 0), flags, text)
        content = QRect(0, 0, max(icon.width(), label.width()), icon.height() + label.height() + spacing)
        content.moveCenter(viewport.center())

        painter.drawPixmap(content.left() + (content.width() - icon.width()) // 2, content.top(), icon)

        label.moveTop(content.top() + icon.height() + spacing)
        label.setWidth(content.width())
        painter.drawText(label, flags, text)
