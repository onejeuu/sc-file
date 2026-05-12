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
    QPixmap,
    QResizeEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileIconProvider,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from scfile.gui.shared import utils
from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Colors, Styles


_ENV_STUB = "."
_ENV_MAPPING = {
    Path(os.environ.get("APPDATA", _ENV_STUB)): "%APPDATA%",
    Path(os.environ.get("LOCALAPPDATA", _ENV_STUB)): "%LOCALAPPDATA%",
    Path.home(): "~",
}
_ENV_MAPPING = {k: v for k, v in _ENV_MAPPING.items() if k.exists()}


class SourcesWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet(Styles.LIST)
        self.setMinimumWidth(320)

        self.icon_provider = QFileIconProvider()

        self._setup_placeholder()

        # TODO: clipboard paste support

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
        self._update_placeholder()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        self.add_sources([url.toLocalFile() for url in event.mimeData().urls()])
        event.acceptProposedAction()
        self._update_placeholder()

    def _setup_placeholder(self):
        self.placeholder = QWidget(self.viewport())
        self.placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.placeholder.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(self.placeholder)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        color = QColor(Colors.TEXT.dark)

        self.placeholder_icon = QLabel()
        aspect = Qt.AspectRatioMode.KeepAspectRatio
        mode = Qt.TransformationMode.SmoothTransformation
        raw_pixmap = QPixmap(str(utils.get_resource("assets/upload.png")))
        raw_pixmap = raw_pixmap.scaled(64, 64, aspect, mode)

        tinted = QPixmap(raw_pixmap.size())
        tinted.fill(Qt.GlobalColor.transparent)
        p = QPainter(tinted)
        p.drawPixmap(0, 0, raw_pixmap)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.fillRect(tinted.rect(), color)
        p.end()

        self.placeholder_icon.setPixmap(tinted)
        self.placeholder_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_content = Strings.get("drop_hint").replace("\n", "<br>")
        self.placeholder_text = QLabel(text_content)
        self.placeholder_text.setFont(QFont("Segoe UI", 12))
        self.placeholder_text.setStyleSheet(f"color: {Colors.TEXT.dark}; border: none;")
        self.placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.placeholder_icon)
        layout.addWidget(self.placeholder_text)

        self.placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._update_placeholder()

    def _update_placeholder(self):
        self.placeholder.setVisible(self.count() == 0)
        if self.placeholder.isVisible():
            self.placeholder.resize(self.viewport().size())

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.placeholder.resize(self.viewport().size())
