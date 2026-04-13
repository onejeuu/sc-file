from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from scfile.consts import NBT_FILENAMES
from scfile.core.context.options import UserOptions
from scfile.gui import consts
from scfile.gui.components import FileListWidget
from scfile.gui.consts import Styles
from scfile.gui.worker import ConvertWorker, OutputConfig


class ConverterTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.main_content_layout = QHBoxLayout(self)
        self.main_content_layout.setContentsMargins(10, 10, 10, 10)

        self.left_column = QVBoxLayout()
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

        self.left_column.addLayout(header_layout)
        self.left_column.addWidget(self.file_list, 1)

        self.right_column = QVBoxLayout()
        right_label = QLabel("Настройки")
        right_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        self.right_column.addWidget(right_label)

        self.feature_widgets = {}
        self.type_checkboxes = {}

        for ft in consts.FILE_TYPES:
            group_widget = QWidget()
            group_layout = QVBoxLayout(group_widget)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(0)

            cb_type = QCheckBox(ft.label)
            cb_type.setStyleSheet(Styles.CHECKBOX)
            cb_type.setChecked(True)
            self.type_checkboxes[ft.id] = cb_type

            sub_options = QWidget()
            sub_layout = QVBoxLayout(sub_options)
            sub_layout.setContentsMargins(26, 4, 0, 8)
            sub_layout.setSpacing(2)

            if ft.id == "models":
                fmt_box = QHBoxLayout()
                self.fmt_combo = QComboBox()

                for fmt in consts.MODEL_FORMATS:
                    self.fmt_combo.addItem(str(fmt), fmt)

                self.fmt_combo.currentIndexChanged.connect(self._update_feature_availability)
                fmt_box.addWidget(self.fmt_combo)
                sub_layout.addLayout(fmt_box)

            for feat_id, feat_title in ft.feature_map.items():
                cb_feat = QCheckBox(feat_title)
                cb_feat.setStyleSheet(Styles.CHECKBOX)
                sub_layout.addWidget(cb_feat)
                self.feature_widgets[feat_id] = cb_feat

            cb_type.toggled.connect(sub_options.setEnabled)
            group_layout.addWidget(cb_type)

            suffix_label = QLabel(", ".join(ft.suffixes))
            suffix_label.setStyleSheet("color: #5c6370; font-size: 10px; margin-left: 26px;")
            group_layout.addWidget(suffix_label)

            group_layout.addWidget(sub_options)
            self.right_column.addWidget(group_widget)

        self.right_column.addSpacing(10)
        output_label = QLabel("Путь сохранения")
        output_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #abb2bf;")
        self.right_column.addWidget(output_label)

        self.mode_group = QButtonGroup(self)

        self.radio_same_dir = QRadioButton("В папку с оригинальным файлом")
        self.radio_same_dir.setStyleSheet(Styles.RADIO)
        self.radio_same_dir.setChecked(True)
        self.mode_group.addButton(self.radio_same_dir)
        self.right_column.addWidget(self.radio_same_dir)

        self.path_row_widget = QWidget()
        path_row_layout = QHBoxLayout(self.path_row_widget)
        path_row_layout.setContentsMargins(0, 0, 0, 0)
        path_row_layout.setSpacing(8)

        self.radio_custom_dir = QRadioButton("")
        self.radio_custom_dir.setFixedWidth(16)
        self.radio_custom_dir.setStyleSheet(Styles.RADIO)
        self.mode_group.addButton(self.radio_custom_dir)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Укажите путь...")
        self.path_edit.setStyleSheet(Styles.INPUT)

        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self._browse_output_path)

        self.path_row_widget.mousePressEvent = lambda e: self.radio_custom_dir.setChecked(True)

        path_row_layout.addWidget(self.radio_custom_dir)
        path_row_layout.addWidget(self.path_edit)
        path_row_layout.addWidget(self.browse_btn)

        self.right_column.addWidget(self.path_row_widget)

        self.structure_container = QWidget()
        structure_layout = QVBoxLayout(self.structure_container)
        structure_layout.setContentsMargins(26, 0, 0, 0)
        structure_layout.setSpacing(4)

        self.radio_flat = QRadioButton("В одну папку")
        self.radio_tree = QRadioButton("Сохранять структуру подпапок")
        self.radio_flat.setStyleSheet(Styles.RADIO)
        self.radio_tree.setStyleSheet(Styles.RADIO)
        self.radio_flat.setChecked(True)

        structure_group = QButtonGroup(self)
        structure_group.addButton(self.radio_flat)
        structure_group.addButton(self.radio_tree)

        structure_layout.addWidget(self.radio_flat)
        structure_layout.addWidget(self.radio_tree)
        self.right_column.addWidget(self.structure_container)

        self.radio_same_dir.toggled.connect(self._sync_output_ui)
        self.radio_custom_dir.toggled.connect(self._sync_output_ui)

        self.right_column.addStretch()

        self.convert_btn = QPushButton("КОНВЕРТИРОВАТЬ")
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet(Styles.CONVERT)
        self.convert_btn.clicked.connect(self._convert)
        self.right_column.addWidget(self.convert_btn)

        self.main_content_layout.addLayout(self.left_column, stretch=2)
        self.main_content_layout.addLayout(self.right_column, stretch=1)

        self.parent_layout = QVBoxLayout()
        self._sync_output_ui()
        self._update_convert_button_state()
        self._update_feature_availability()

    def _sync_output_ui(self):
        is_custom = self.radio_custom_dir.isChecked()
        self.path_edit.setEnabled(is_custom)
        self.browse_btn.setEnabled(is_custom)
        self.structure_container.setEnabled(is_custom)

    def _convert(self) -> None:
        allowed_exts = set()
        nbt_names = set()

        if self.type_checkboxes["nbt"].isChecked():
            nbt_names = set(NBT_FILENAMES)

        for ft in consts.FILE_TYPES:
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

        self.convert_btn.setEnabled(False)

        self._thread = QThread()
        self._worker = ConvertWorker(paths, options, output, checker)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(lambda: self.convert_btn.setEnabled(True))
        self._thread.start()

    def _update_feature_availability(self):
        fmt = self.fmt_combo.currentData()
        if not fmt:
            return

        for fid, widget in self.feature_widgets.items():
            is_supported = any(f.id == fid for f in fmt.features)

            widget.setEnabled(is_supported)
            if not is_supported:
                widget.setChecked(False)

    def _update_convert_button_state(self):
        ok = self.file_list.count() > 0
        self.convert_btn.setEnabled(ok)
        self.convert_btn.setToolTip("" if ok else "Добавьте источники для конвертации")

    def _open_file_dialog(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Файлы")
        if fs:
            self.file_list.add_paths(fs)

    def _open_directory_dialog(self):
        d = QFileDialog.getExistingDirectory(self, "Папка")
        if d:
            self.file_list.add_paths([d])

    def _browse_output_path(self):
        d = QFileDialog.getExistingDirectory(self, "Папка результатов")
        if d:
            self.path_edit.setText(d)
