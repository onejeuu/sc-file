import os
from pathlib import Path

from PySide6.QtCore import QFileInfo, Qt
from PySide6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QFont,
    QKeyEvent,
    QPainter,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileIconProvider,
    QListWidget,
    QListWidgetItem,
    QMenu,
)

from .strings import Strings
from .styles import Styles


_ENV_STUB = "."
_ENV_MAPPING = {
    Path(os.environ.get("APPDATA", _ENV_STUB)): "%APPDATA%",
    Path(os.environ.get("LOCALAPPDATA", _ENV_STUB)): "%LOCALAPPDATA%",
    Path.home(): "~",
}
_ENV_MAPPING = {k: v for k, v in _ENV_MAPPING.items() if k.exists()}


class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet(Styles.LIST)
        self.icon_provider = QFileIconProvider()

    def _normalize_path(self, source: str) -> str:
        path = Path(source).resolve()

        for env, alias in _ENV_MAPPING.items():
            if env != Path(_ENV_STUB) and path.is_relative_to(env):
                relative = path.relative_to(env)
                return (Path(alias) / relative).as_posix()

        return path.as_posix()

    def add_sources(self, sources: list[str]):
        for source in sources:
            if not source:
                continue

            normalized = self._normalize_path(source)

            existing = self.findItems(normalized, Qt.MatchFlag.MatchExactly)
            if existing:
                continue

            item = QListWidgetItem(normalized)
            item.setData(Qt.ItemDataRole.UserRole, source)
            item.setIcon(self.icon_provider.icon(QFileInfo(source)))
            self.addItem(item)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            menu = QMenu(self)
            remove_action = QAction(Strings.get("action_remove"), self)
            remove_action.triggered.connect(self.remove_selected)
            menu.addAction(remove_action)
            menu.exec(event.globalPos())

    def remove_selected(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        self.add_sources([url.toLocalFile() for url in event.mimeData().urls()])
        event.acceptProposedAction()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setPen(QColor("#5c6370"))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(self.viewport().rect(), Qt.AlignmentFlag.AlignCenter, Strings.get("drop_hint"))
