import os
from pathlib import Path

from PySide6.QtCore import QFileInfo, QMimeData, Qt, QTimer, Signal
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
from scfile.gui.shared.strings import Str
from scfile.gui.shared.styles import Colors, Styles
from scfile.utils import files


_ENV_STUB = "."
_ENV_MAPPING = {
    Path(os.environ.get("APPDATA", _ENV_STUB)): "%APPDATA%",
    Path(os.environ.get("LOCALAPPDATA", _ENV_STUB)): "%LOCALAPPDATA%",
    Path.home(): "~",
}
_ENV_MAPPING = {k: v for k, v in _ENV_MAPPING.items() if k.exists() and k != Path(_ENV_STUB)}


def normalize_path(source: types.PathLike) -> str:
    path = Path(source).resolve()

    for env, alias in _ENV_MAPPING.items():
        if path.is_relative_to(env):
            relative = path.relative_to(env)
            return (Path(alias) / relative).as_posix()

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
        self._placeholder_text = Str.get("drop_hint")

    def add_sources(self, sources: types.FilesSources):
        for source in sources:
            if not source:
                continue

            path = normalize_path(source)
            existing = self.findItems(path, Qt.MatchFlag.MatchExactly)
            if existing:
                continue

            item = QListWidgetItem(path)
            item.setData(Qt.ItemDataRole.UserRole, source)
            item.setIcon(self.icon_provider.icon(QFileInfo(source)))
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
            remove_action = QAction(Str.get("action_remove"), self)
            remove_action.triggered.connect(self._remove_selected)
            menu.addAction(remove_action)
            menu.exec(event.globalPos())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            self._remove_selected()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self._paste_from_clipboard()
            event.accept()
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if self._add_mime(event.mimeData()):
            event.acceptProposedAction()

    def _prepare_placeholder_icon(self) -> QPixmap:
        aspect = Qt.AspectRatioMode.KeepAspectRatio
        mode = Qt.TransformationMode.SmoothTransformation
        raw = QPixmap(str(files.get_resource("assets/upload.png"))).scaled(64, 64, aspect, mode)

        tinted = QPixmap(raw.size())
        tinted.fill(Qt.GlobalColor.transparent)

        paint = QPainter(tinted)
        paint.drawPixmap(0, 0, raw)
        paint.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        paint.fillRect(tinted.rect(), QColor(Colors.TEXT.dark))
        paint.end()
        return tinted

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.count() > 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        viewport = self.viewport().rect()

        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        painter.setPen(QColor(Colors.TEXT.dark))

        fm = painter.fontMetrics()
        flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
        text_rect = fm.boundingRect(viewport, flags, self._placeholder_text)

        spacing = 8
        icon_size = self._placeholder_icon.size()
        total_height = icon_size.height() + spacing + text_rect.height()

        start_y = (viewport.height() - total_height) // 2

        icon_x = (viewport.width() - icon_size.width()) // 2
        painter.drawPixmap(icon_x, start_y, self._placeholder_icon)

        text_y_offset = start_y + icon_size.height() + spacing
        draw_text_rect = viewport.adjusted(0, text_y_offset, 0, 0)

        flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        painter.drawText(draw_text_rect, flags, self._placeholder_text)

        painter.end()
