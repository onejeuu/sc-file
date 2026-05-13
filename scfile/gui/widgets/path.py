from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget

from scfile.enums import L
from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Styles


class PathInputWidget(QWidget):
    changed = Signal(str)

    def __init__(self, placeholder: str, caption: str, parent=None):
        super().__init__(parent)
        self.caption = caption
        self._setup_ui(placeholder)

    def _setup_ui(self, placeholder):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setStyleSheet(Styles.INPUT)
        self.line_edit.editingFinished.connect(lambda: self.changed.emit(self.line_edit.text()))

        self.browse_btn = QPushButton("...")
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setFixedSize(30, 30)
        self.browse_btn.setToolTip(Strings.get("tooltip_path_browse"))

        self.browse_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browse_btn.customContextMenuRequested.connect(self._open_in_explorer)
        self.browse_btn.clicked.connect(self._browse)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_btn)

    def _browse(self):
        directory = QFileDialog.getExistingDirectory(self, self.caption)
        if directory:
            self.line_edit.setText(directory)
            self.changed.emit(directory)

    def _open_in_explorer(self):
        text = self.line_edit.text().strip()

        if not text:
            return

        try:
            path = Path(text)

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
