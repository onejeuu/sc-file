from pathlib import Path
from typing import Literal

from PySide6.QtCore import QMimeData, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget

from scfile.enums import L
from scfile.gui.shared import strings
from scfile.gui.shared.styles import Styles


PathMode = Literal["directory", "open", "save"]


class _PathLineEdit(QLineEdit):
    path_set = Signal(str)

    @staticmethod
    def _local_path(data: QMimeData) -> str | None:
        if data.hasUrls():
            for url in data.urls():
                if url.isLocalFile():
                    return url.toLocalFile()

        if data.hasText():
            url = QUrl(data.text().strip())
            if url.isLocalFile():
                return url.toLocalFile()

        return None

    def insertFromMimeData(self, data: QMimeData) -> None:
        if path := self._local_path(data):
            self.insert(path)
        else:
            super().insertFromMimeData(data)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._local_path(event.mimeData()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self._local_path(event.mimeData()):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if path := self._local_path(event.mimeData()):
            self.setText(path)
            self.path_set.emit(path)
            event.acceptProposedAction()


class PathInputWidget(QWidget):
    changed = Signal(str)

    def __init__(
        self,
        placeholder: str,
        caption: str,
        mode: PathMode = "directory",
        file_filter: str = "",
        default_suffix: str = "",
        initial_path: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.caption = caption
        self.mode = mode
        self.file_filter = file_filter
        self.default_suffix = default_suffix
        self.initial_path = initial_path
        self._setup_ui(placeholder)

    def _setup_ui(self, placeholder):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.line_edit = _PathLineEdit()
        self.line_edit.setAcceptDrops(True)
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setStyleSheet(Styles.INPUT)
        self.line_edit.editingFinished.connect(self._emit_changed)
        self.line_edit.path_set.connect(self.changed.emit)

        self.browse_btn = QPushButton("...")
        self.browse_btn.setStyleSheet(Styles.BUTTON)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setFixedSize(30, 30)
        tooltip = "tooltip.path_browse" if self.mode == "directory" else "tooltip.file_browse"
        self.browse_btn.setToolTip(strings.get(tooltip))

        self.browse_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browse_btn.customContextMenuRequested.connect(self._open_in_explorer)
        self.browse_btn.clicked.connect(self._browse)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_btn)

    def _browse(self):
        initial_path = self.text().strip() or self.initial_path

        match self.mode:
            case "open":
                path, _ = QFileDialog.getOpenFileName(self, self.caption, initial_path, self.file_filter)
            case "save":
                path, _ = QFileDialog.getSaveFileName(self, self.caption, initial_path, self.file_filter)
                if path and self.default_suffix and not Path(path).suffix:
                    path += self.default_suffix
            case _:
                path = QFileDialog.getExistingDirectory(self, self.caption, initial_path)

        if path:
            self.line_edit.setText(path)
            self.changed.emit(path)

    def _emit_changed(self) -> None:
        text = self.line_edit.text().strip()
        url = QUrl(text)

        if url.isLocalFile():
            text = url.toLocalFile()
            self.line_edit.setText(text)

        self.changed.emit(text)

    def _open_in_explorer(self):
        text = self.line_edit.text().strip()

        if not text:
            return

        try:
            path = Path(text)
            if self.mode != "directory" and (path.is_file() or path.suffix):
                path = path.parent

            if not path.exists() and not path.is_file():
                path.mkdir(exist_ok=True, parents=True)

            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        except Exception as err:
            print(L.ERROR, repr(err))

    def text(self) -> str:
        return self.line_edit.text()

    def setText(self, text: str):
        self.line_edit.setText(text)

    @property
    def textChanged(self):
        return self.line_edit.textChanged
