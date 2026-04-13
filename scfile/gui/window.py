import os
import sys
from typing import NamedTuple

from PySide6.QtCore import QFileInfo, Qt
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
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from scfile import __version__
from scfile.consts import NBT_FILENAMES

from . import utils


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
        self.setWindowTitle(f"scfile {__version__}")
        self.resize(1000, 700)
        self.setWindowIcon(QIcon(str(utils.get_resource("assets/scfile.ico"))))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        outer_layout = QVBoxLayout(central_widget)

        main_content_layout = QHBoxLayout()

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
        right_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
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

        for ft in FILE_TYPES:
            group_widget = QWidget()
            group_layout = QVBoxLayout(group_widget)
            group_layout.setContentsMargins(0, 0, 0, 4)
            group_layout.setSpacing(2)

            cb_type = QCheckBox(ft.label)
            cb_type.setStyleSheet(checkbox_style + "QCheckBox { font-weight: bold; }")
            cb_type.setChecked(True)

            suffix_label = QLabel(", ".join(ft.suffixes))
            suffix_label.setWordWrap(True)
            suffix_label.setStyleSheet("color: #5c6370; font-size: 10px; margin-left: 26px;")

            group_layout.addWidget(cb_type)
            group_layout.addWidget(suffix_label)

            sub_options = QWidget()
            sub_layout = QVBoxLayout(sub_options)
            sub_layout.setContentsMargins(26, 5, 0, 12)
            sub_layout.setSpacing(4)

            if ft.id == "models":
                fmt_box = QHBoxLayout()
                fmt_label = QLabel("Формат:")
                fmt_label.setStyleSheet("color: #abb2bf; font-size: 11px;")
                self.fmt_combo = QComboBox()
                for f in FORMATS:
                    self.fmt_combo.addItem(get_format_display_text(f), f)
                self.fmt_combo.currentIndexChanged.connect(self._update_feature_availability)
                fmt_box.addWidget(fmt_label)
                fmt_box.addWidget(self.fmt_combo)
                sub_layout.addLayout(fmt_box)

            for feat_id, feat_label in ft.features.items():
                cb_feat = QCheckBox(feat_label)
                cb_feat.setStyleSheet(checkbox_style)
                sub_layout.addWidget(cb_feat)
                self.feature_widgets[feat_id] = cb_feat

            cb_type.toggled.connect(sub_options.setEnabled)
            right_column.addWidget(group_widget)
            right_column.addWidget(sub_options)

        right_column.addSpacing(10)
        output_label = QLabel("Путь сохранения")
        output_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #abb2bf;")
        right_column.addWidget(output_label)

        self.out_same_dir = QCheckBox("В папку с оригиналом")
        self.out_same_dir.setStyleSheet(checkbox_style)
        self.out_same_dir.setChecked(True)
        right_column.addWidget(self.out_same_dir)

        self.custom_path_widget = QWidget()
        custom_path_layout = QVBoxLayout(self.custom_path_widget)
        custom_path_layout.setContentsMargins(26, 0, 0, 0)

        path_input_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Укажите путь...")
        self.path_edit.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                color: #abb2bf;
                border: 1px solid #555;
                padding: 4px;
            }
            QLineEdit:disabled {
                background: #222;
                color: #555;
                border: 1px solid #333;
            }
        """)

        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self._browse_output_path)

        path_input_layout.addWidget(self.path_edit)
        path_input_layout.addWidget(self.browse_btn)
        custom_path_layout.addLayout(path_input_layout)

        self.structure_group = QButtonGroup(self)
        self.radio_flat = QRadioButton("В одну папку")
        self.radio_tree = QRadioButton("Сохранять структуру подпапок")
        self.radio_flat.setStyleSheet(radio_style)
        self.radio_tree.setStyleSheet(radio_style)
        self.radio_flat.setChecked(True)

        self.structure_group.addButton(self.radio_flat)
        self.structure_group.addButton(self.radio_tree)

        custom_path_layout.addWidget(self.radio_flat)
        custom_path_layout.addWidget(self.radio_tree)

        right_column.addWidget(self.custom_path_widget)
        self.out_same_dir.toggled.connect(lambda checked: self.custom_path_widget.setEnabled(not checked))
        self.custom_path_widget.setEnabled(False)

        right_column.addStretch()

        main_content_layout.addLayout(left_column, stretch=2)
        main_content_layout.addLayout(right_column, stretch=1)

        self.convert_btn = QPushButton("КОНВЕРТИРОВАТЬ")
        self.convert_btn.setMinimumHeight(60)
        self.convert_btn.setStyleSheet("""
            QPushButton { background-color: #FFD666; color: black; font-weight: bold; border: none; font-size: 16px; }
            QPushButton:hover { background-color: #ffe08a; }
            QPushButton:disabled { background-color: #444; color: #888; }
        """)

        outer_layout.addLayout(main_content_layout)
        outer_layout.addWidget(self.convert_btn)

        self._update_convert_button_state()
        self._update_feature_availability()

    def _update_feature_availability(self):
        fmt_data = self.fmt_combo.currentData()
        for feat_id, widget in self.feature_widgets.items():
            is_supported = fmt_data.get(feat_id, True)
            widget.setEnabled(is_supported)
            if not is_supported:
                widget.setChecked(False)

    def _update_convert_button_state(self):
        has_files = self.file_list.count() > 0
        self.convert_btn.setEnabled(has_files)
        self.convert_btn.setToolTip("" if has_files else "Выберите файлы для конвертации")

    def _browse_output_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку выхода")
        if directory:
            self.path_edit.setText(directory)

    def _open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы")
        if files:
            self.file_list.add_paths(files)

    def _open_directory_dialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory:
            self.file_list.add_paths([directory])


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
