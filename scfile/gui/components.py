import os

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

from scfile.gui.consts import Styles


class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet(Styles.LIST)
        self.icon_provider = QFileIconProvider()

    def _normalize_path(self, path: str) -> str:
        path = os.path.normpath(path)
        mapping = {"APPDATA": "%APPDATA%", "LOCALAPPDATA": "%LOCALAPPDATA%", "USERPROFILE": "~"}
        for env_key, alias in mapping.items():
            env_val = os.environ.get(env_key)
            if env_val and path.startswith(env_val):
                return path.replace(env_val, alias, 1)
        return path

    def add_paths(self, paths: list[str]):
        for path in paths:
            if not path:
                continue

            normalized = self._normalize_path(path)

            existing = self.findItems(normalized, Qt.MatchFlag.MatchExactly)
            if existing:
                continue

            item = QListWidgetItem(normalized)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setIcon(self.icon_provider.icon(QFileInfo(path)))
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
            remove_action = QAction("Удалить из списка", self)
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
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_paths(paths)
        event.acceptProposedAction()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setPen(QColor("#5c6370"))
            painter.setFont(QFont("Segoe UI", 12))

            hint_text = "Добавьте файлы/папки кнопками выше\nили перетащите их сюда (drag & drop)"
            painter.drawText(self.viewport().rect(), Qt.AlignmentFlag.AlignCenter, hint_text)
