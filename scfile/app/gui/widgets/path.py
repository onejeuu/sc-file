from pathlib import Path
from typing import Literal, override

from PySide6.QtCore import QMimeData, QSignalBlocker, Qt, QUrl, Signal
from PySide6.QtGui import (
    QDesktopServices,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from scfile.app.gui import strings
from scfile.app.gui.styles import Colors, Styles


type PathMode = Literal["directory", "open", "save"]


DIALOG_MODES = {
    "directory": (QFileDialog.FileMode.Directory, QFileDialog.AcceptMode.AcceptOpen),
    "open": (QFileDialog.FileMode.ExistingFile, QFileDialog.AcceptMode.AcceptOpen),
    "save": (QFileDialog.FileMode.AnyFile, QFileDialog.AcceptMode.AcceptSave),
}


def _local_file(data: QMimeData) -> str | None:
    if data.hasUrls():
        for url in data.urls():
            if url.isLocalFile():
                return url.toLocalFile()


def _local_path(data: QMimeData) -> str | None:
    if path := _local_file(data):
        return path

    if data.hasText():
        text = data.text().strip()
        if not text:
            return None

        url = QUrl(text)
        if url.isLocalFile():
            return url.toLocalFile()

    return None


def _normalize_path(text: str | None) -> str:
    return (text or "").replace("\\", "/")


class PathLineEdit(QLineEdit):
    activated = Signal()
    dropped = Signal()
    value_changed = Signal(str)
    reset_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._restoring = False
        self.textChanged.connect(self._normalize_text)

    def _normalize_text(self, text: str) -> None:
        normalized = _normalize_path(text)
        if normalized != text:
            cursor = self.cursorPosition()
            selection_start = self.selectionStart()
            selection_length = len(self.selectedText()) if selection_start >= 0 else 0
            modified = self.isModified()

            with QSignalBlocker(self):
                self.setText(normalized)
                self.setModified(modified)

            if selection_start >= 0:
                self.setSelection(selection_start, selection_length)
            else:
                self.setCursorPosition(cursor)

        self.value_changed.emit(normalized)

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.activated.emit()
        super().mousePressEvent(event)

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Paste):
            if path := _local_file(QApplication.clipboard().mimeData()):
                self.selectAll()
                self.insert(path)
                event.accept()
                return

        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if self._restoring:
                event.accept()
                return

            if not self.text():
                self.reset_requested.emit()
                self._restoring = True
                event.accept()
                return

        super().keyPressEvent(event)

    @override
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self._restoring = False

        super().keyReleaseEvent(event)

    def insertFromMimeData(self, data: QMimeData) -> None:
        if path := _local_path(data):
            self.insert(path)
        else:
            self.insert(data.text())

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if _local_path(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    @override
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if _local_path(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    @override
    def dropEvent(self, event: QDropEvent) -> None:
        if path := _local_path(event.mimeData()):
            self.setText(path)
            self.dropped.emit()
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class PathInputWidget(QWidget):
    activated = Signal()
    changed = Signal(str)
    text_changed = Signal(str)
    reset_requested = Signal()

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
        self._initial_path = _normalize_path(initial_path)

        self._build_ui(placeholder)

    def _build_ui(self, placeholder: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.line_edit = PathLineEdit()
        self.line_edit.setAcceptDrops(True)
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setStyleSheet(Styles.INPUT)

        self.line_edit.activated.connect(self.activated)
        self.line_edit.editingFinished.connect(self._emit_edited)
        self.line_edit.value_changed.connect(self.text_changed)
        self.line_edit.dropped.connect(self._emit_changed)
        self.line_edit.reset_requested.connect(self.reset_requested)

        self.browse_btn = QPushButton("...")
        self.browse_btn.setStyleSheet(Styles.BUTTON)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setFixedSize(30, 30)

        tooltip = "tooltip.browse.directory" if self.mode == "directory" else "tooltip.browse.file"
        self.browse_btn.setToolTip(strings.get(tooltip))

        self.browse_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browse_btn.customContextMenuRequested.connect(self._open_in_explorer)
        self.browse_btn.clicked.connect(self._browse)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_btn)

    def _browse(self) -> None:
        file_mode, accept_mode = DIALOG_MODES[self.mode]
        initial_path = self.value.strip() or self.initial_path

        dialog = QFileDialog(self, self.caption, initial_path)
        dialog.setFileMode(file_mode)
        dialog.setAcceptMode(accept_mode)
        dialog.setNameFilter(self.file_filter)
        dialog.setDefaultSuffix(self.default_suffix.removeprefix("."))

        if dialog.exec():
            path = dialog.selectedFiles()[0]
            self.value = path
            self._emit_changed()

    def _emit_changed(self) -> None:
        self.changed.emit(self.value.strip())

    def _emit_edited(self) -> None:
        if self.line_edit.isModified():
            self._emit_changed()

    def _open_in_explorer(self) -> None:
        value = self.value.strip()

        if not value:
            return

        path = Path(value)

        if self.mode != "directory" and (path.is_file() or path.suffix):
            path = path.parent

        while not path.exists() and path != path.parent:
            path = path.parent

        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @property
    def value(self) -> str:
        return self.line_edit.text()

    @value.setter
    def value(self, text: str) -> None:
        self.line_edit.setText(text)

    @property
    def initial_path(self) -> str:
        return self._initial_path

    @initial_path.setter
    def initial_path(self, path: str) -> None:
        self._initial_path = _normalize_path(path)

    @property
    def invalid(self) -> bool:
        return bool(self.line_edit.property("invalid"))

    @invalid.setter
    def invalid(self, value: bool) -> None:
        self.line_edit.setProperty("invalid", value)

        style = self.line_edit.style()
        style.unpolish(self.line_edit)
        style.polish(self.line_edit)

    @property
    def read_only(self) -> bool:
        return self.line_edit.isReadOnly()

    @read_only.setter
    def read_only(self, value: bool) -> None:
        self.line_edit.setReadOnly(value)
        self.browse_btn.setEnabled(not value)

    @property
    def placeholder(self) -> str:
        return self.line_edit.placeholderText()

    @placeholder.setter
    def placeholder(self, text: str) -> None:
        self.line_edit.setPlaceholderText(text)


class PathField(QWidget):
    activated = Signal()
    changed = Signal(str)
    text_changed = Signal(str)
    reset_requested = Signal()

    def __init__(
        self,
        label: str,
        placeholder: str,
        caption: str,
        *,
        required: bool = True,
        mode: PathMode = "directory",
        file_filter: str = "",
        default_suffix: str = "",
        initial_path: str = "",
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel(label)

        if required:
            title.setText(f'{label} <span style="color: {Colors.ERROR}">*</span>')
            title.setToolTip(strings.get("tooltip.form.required"))

        title.setStyleSheet(Styles.LABEL)

        self.input = PathInputWidget(
            placeholder=placeholder,
            caption=caption,
            mode=mode,
            file_filter=file_filter,
            default_suffix=default_suffix,
            initial_path=initial_path,
        )

        self.input.activated.connect(self.activated.emit)
        self.input.changed.connect(self.changed.emit)
        self.input.text_changed.connect(self.text_changed.emit)
        self.input.reset_requested.connect(self.reset_requested)

        layout.addWidget(title)
        layout.addWidget(self.input)

        self.error = QLabel()
        self.error.setStyleSheet(Styles.ERROR)
        self.error.setWordWrap(True)
        self.error.hide()

        layout.addWidget(self.error)

    @property
    def value(self) -> str:
        return self.input.value

    @value.setter
    def value(self, text: str) -> None:
        self.input.value = text

    @property
    def invalid(self) -> bool:
        return self.input.invalid

    @invalid.setter
    def invalid(self, value: bool) -> None:
        self.input.invalid = value

    def set_error(self, text: str | None) -> None:
        self.invalid = text is not None
        self.error.setText(text or "")
        self.error.setVisible(text is not None)

    @property
    def initial_path(self) -> str:
        return self.input.initial_path

    @initial_path.setter
    def initial_path(self, path: str) -> None:
        self.input.initial_path = path

    @property
    def read_only(self) -> bool:
        return self.input.read_only

    @read_only.setter
    def read_only(self, value: bool) -> None:
        self.input.read_only = value
