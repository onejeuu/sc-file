import os
import sys
from pathlib import Path
from typing import NamedTuple

from PySide6.QtCore import QFileInfo, Qt, QThread
from PySide6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QFont,
    QIcon,
    QKeyEvent,
    QPainter,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFileIconProvider,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from scfile import __version__
from scfile.consts import NBT_FILENAMES
from scfile.core.context.options import UserOptions

from . import utils
from .worker import ConvertWorker, OutputConfig


FEATURE_ICONS = {
    "skeleton": "🦴",
    "animation": "🌀",
}


class FileType(NamedTuple):
    id: str
    label: str
    suffixes: list[str]
    features: dict[str, str] = {}


FILE_TYPES = [
    FileType(
        "models",
        "🧊 Модели",
        [".mcsa", ".mcsb", ".mcvd"],
        features={"skeleton": "🦴 Скелет", "animation": "🌀 Анимация"},
    ),
    FileType("textures", "🧱 Текстуры", [".ol"]),
    FileType("images", "🖼 Изображения", [".mic"]),
    FileType("texarr", "🗃️ Массив текстур", [".texarr"]),
    FileType("nbt", "⚙️ NBT Данные", list(sorted(NBT_FILENAMES))),
]

FORMATS = [
    {"name": "OBJ", "skeleton": False, "animation": False},
    {"name": "GLB", "skeleton": True, "animation": True},
    {"name": "DAE", "skeleton": True, "animation": False},
    {"name": "MS3D", "skeleton": True, "animation": False},
]


def get_format_display_text(fmt: dict) -> str:
    icons = [FEATURE_ICONS[key] for key in FEATURE_ICONS if fmt.get(key)]
    return f"{fmt['name']} {' '.join(icons)}".strip()


class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet("""
            QListWidget {
                background: #2b2b2b;
                color: #abb2bf;
                border: 1px solid #555;
                outline: none;
                font-size: 12px;
            }
            QListWidget::item { padding: 3px 5px; }
            QListWidget::item:selected { background: #3e4451; color: #ffffff; }
        """)
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(str(utils.get_resource("assets/scfile.ico"))))
        self.setWindowTitle(f"scfile {__version__}")
        self.resize(1000, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        outer_layout = QVBoxLayout(central_widget)

        self.splitter = QSplitter(Qt.Orientation.Vertical)

        content_pane = QWidget()
        main_content_layout = QHBoxLayout(content_pane)
        main_content_layout.setContentsMargins(0, 0, 0, 0)

        left_column = QVBoxLayout()
        header_layout = QHBoxLayout()
        left_label = QLabel("Источники")
        left_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        btn_layout = QHBoxLayout()
        add_file_btn = QPushButton("+ Файлы")
        add_file_btn.clicked.connect(self._open_file_dialog)
        add_dir_btn = QPushButton("+ Папка")
        add_dir_btn.clicked.connect(self._open_directory_dialog)
        btn_layout.addWidget(add_file_btn)
        btn_layout.addWidget(add_dir_btn)

        header_layout.addWidget(left_label)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)

        self.file_list = FileListWidget()
        self.file_list.model().rowsInserted.connect(self._update_convert_button_state)
        self.file_list.model().rowsRemoved.connect(self._update_convert_button_state)

        left_column.addLayout(header_layout)
        left_column.addWidget(self.file_list, 1)

        right_column = QVBoxLayout()
        right_label = QLabel("Настройки")
        right_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        right_column.addWidget(right_label)

        checkbox_style = """
            QCheckBox { color: #abb2bf; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #555; background: #2b2b2b; }
            QCheckBox::indicator:checked { background: #FFD666; border: 1px solid #FFD666; }
            QCheckBox::indicator:unchecked:hover { border: 1px solid #FFD666; }
            QCheckBox:disabled { color: #555; }
            QCheckBox::indicator:disabled { background: #1a1a1a; border: 1px solid #333; }
        """
        radio_style = """
            QRadioButton { color: #abb2bf; spacing: 8px; font-size: 11px; }
            QRadioButton::indicator { width: 14px; height: 14px; border-radius: 7px; border: 1px solid #555; background: #2b2b2b; }
            QRadioButton::indicator:checked { background: #FFD666; border: 1px solid #FFD666; }
            QRadioButton:disabled { color: #555; }
        """

        self.feature_widgets = {}
        self.type_checkboxes = {}

        for ft in FILE_TYPES:
            group_widget = QWidget()
            group_layout = QVBoxLayout(group_widget)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(0)

            cb_type = QCheckBox(ft.label)
            cb_type.setStyleSheet(checkbox_style + "QCheckBox { font-weight: bold; }")
            cb_type.setChecked(True)
            self.type_checkboxes[ft.id] = cb_type

            sub_options = QWidget()
            sub_layout = QVBoxLayout(sub_options)
            sub_layout.setContentsMargins(26, 4, 0, 8)
            sub_layout.setSpacing(2)

            if ft.id == "models":
                fmt_box = QHBoxLayout()
                self.fmt_combo = QComboBox()
                for f in FORMATS:
                    self.fmt_combo.addItem(get_format_display_text(f), f)
                self.fmt_combo.currentIndexChanged.connect(self._update_feature_availability)
                fmt_box.addWidget(self.fmt_combo)
                sub_layout.addLayout(fmt_box)

            for feat_id, feat_label in ft.features.items():
                cb_feat = QCheckBox(feat_label)
                cb_feat.setStyleSheet(checkbox_style)
                sub_layout.addWidget(cb_feat)
                self.feature_widgets[feat_id] = cb_feat

            cb_type.toggled.connect(sub_options.setEnabled)
            group_layout.addWidget(cb_type)

            suffix_label = QLabel(", ".join(ft.suffixes))
            suffix_label.setStyleSheet("color: #5c6370; font-size: 10px; margin-left: 26px;")
            group_layout.addWidget(suffix_label)

            group_layout.addWidget(sub_options)
            right_column.addWidget(group_widget)

        right_column.addSpacing(10)
        output_label = QLabel("Путь сохранения")
        output_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #abb2bf;")
        right_column.addWidget(output_label)

        self.mode_group = QButtonGroup(self)

        self.radio_same_dir = QRadioButton("В папку с оригинальным файлом")
        self.radio_same_dir.setStyleSheet(radio_style)
        self.radio_same_dir.setChecked(True)
        self.mode_group.addButton(self.radio_same_dir)
        right_column.addWidget(self.radio_same_dir)

        custom_path_line = QHBoxLayout()
        custom_path_line.setContentsMargins(0, 0, 0, 0)
        custom_path_line.setSpacing(8)

        self.radio_custom_dir = QRadioButton("")
        self.radio_custom_dir.setFixedWidth(16)
        self.radio_custom_dir.setStyleSheet(radio_style)
        self.mode_group.addButton(self.radio_custom_dir)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Укажите путь...")
        self.path_edit.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a; color: #abb2bf;
                border: 1px solid #555; padding: 4px;
            }
            QLineEdit:disabled { background: #222; color: #555; border: 1px solid #333; }
        """)

        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self._browse_output_path)

        custom_path_line.addWidget(self.radio_custom_dir)
        custom_path_line.addWidget(self.path_edit)
        custom_path_line.addWidget(self.browse_btn)
        right_column.addLayout(custom_path_line)

        self.structure_container = QWidget()
        structure_layout = QVBoxLayout(self.structure_container)
        structure_layout.setContentsMargins(26, 0, 0, 0)
        structure_layout.setSpacing(4)

        self.radio_flat = QRadioButton("В одну папку")
        self.radio_tree = QRadioButton("Сохранять структуру подпапок")
        self.radio_flat.setStyleSheet(radio_style)
        self.radio_tree.setStyleSheet(radio_style)
        self.radio_flat.setChecked(True)

        structure_group = QButtonGroup(self)
        structure_group.addButton(self.radio_flat)
        structure_group.addButton(self.radio_tree)

        structure_layout.addWidget(self.radio_flat)
        structure_layout.addWidget(self.radio_tree)
        right_column.addWidget(self.structure_container)

        def sync_ui():
            is_custom = self.radio_custom_dir.isChecked()
            self.path_edit.setEnabled(is_custom)
            self.browse_btn.setEnabled(is_custom)
            self.structure_container.setEnabled(is_custom)

        self.radio_same_dir.toggled.connect(sync_ui)
        self.radio_custom_dir.toggled.connect(sync_ui)
        sync_ui()

        right_column.addStretch()

        main_content_layout.addLayout(left_column, stretch=2)
        main_content_layout.addLayout(right_column, stretch=1)

        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("""
            QPlainTextEdit {
                background: #1a1a1a; color: #98c379;
                font-family: Consolas, monospace; font-size: 12px;
                border: 1px solid #333;
            }
        """)

        self.splitter.addWidget(content_pane)
        self.splitter.addWidget(self.log_console)
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)

        self.convert_btn = QPushButton("КОНВЕРТИРОВАТЬ")
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet("""
            QPushButton { background: #FFD666; color: black; font-weight: bold; font-size: 15px; border: none; }
            QPushButton:hover { background: #ffe08a; }
            QPushButton:disabled { background: #444; color: #888; }
        """)
        self.convert_btn.clicked.connect(self._convert)

        outer_layout.addWidget(self.splitter)
        outer_layout.addWidget(self.convert_btn)

        self._update_convert_button_state()
        self._update_feature_availability()

    def _convert(self) -> None:
        allowed_exts = set()
        nbt_names = set()

        if self.type_checkboxes["nbt"].isChecked():
            nbt_names = set(NBT_FILENAMES)

        for ft in FILE_TYPES:
            if ft.id != "nbt" and self.type_checkboxes[ft.id].isChecked():
                allowed_exts.update(ft.suffixes)

        def checker(p: Path) -> bool:
            return (p.name in nbt_names) or (p.suffix.lower() in allowed_exts)

        fmt = self.fmt_combo.currentData()
        options = UserOptions(
            model_formats=[fmt["name"].lower()] if fmt else None,
            parse_skeleton=self.feature_widgets["skeleton"].isChecked(),
            parse_animation=self.feature_widgets["animation"].isChecked(),
            overwrite=True,
        )
        output = OutputConfig(
            path=None if self.radio_same_dir.isChecked() else Path(self.path_edit.text()),
            relative=self.radio_tree.isChecked(),
            parent=False,
        )

        paths = [self.file_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.file_list.count())]
        paths = [Path(p) for p in paths]

        self.log_console.clear()
        self.convert_btn.setEnabled(False)

        self._thread = QThread()
        self._worker = ConvertWorker(paths, options, output, checker)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.logs.connect(self.log_console.appendPlainText)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(lambda: self.convert_btn.setEnabled(True))
        self._thread.start()

    def _update_feature_availability(self):
        fmt_data = self.fmt_combo.currentData()
        for fid, w in self.feature_widgets.items():
            ok = fmt_data.get(fid, True)
            w.setEnabled(ok)
            if not ok:
                w.setChecked(False)

    def _update_convert_button_state(self):
        ok = self.file_list.count() > 0
        self.convert_btn.setEnabled(ok)

    def _browse_output_path(self):
        d = QFileDialog.getExistingDirectory(self, "Выход")
        if d:
            self.path_edit.setText(d)

    def _open_file_dialog(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Файлы")
        if fs:
            self.file_list.add_paths(fs)

    def _open_directory_dialog(self):
        d = QFileDialog.getExistingDirectory(self, "Папка")
        if d:
            self.file_list.add_paths([d])


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
