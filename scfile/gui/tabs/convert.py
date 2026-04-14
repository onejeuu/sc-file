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
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from scfile.core.context.options import UserOptions
from scfile.gui.shared import consts
from scfile.gui.shared.consts import FT
from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets import FileListWidget
from scfile.gui.workers.convert import ConvertWorker


class ConverterTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.main_content_layout = QHBoxLayout(self)
        self.main_content_layout.setContentsMargins(10, 10, 10, 10)

        # Create columns
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        self._setup_left_column()
        self._setup_right_column()

        self.main_content_layout.addLayout(self.left_column, stretch=2)
        self.main_content_layout.addLayout(self.right_column, stretch=1)

        # Update state
        self._sync_output_ui()
        self._update_convert_button_state()
        self._update_feature_availability()

    def _setup_left_column(self):
        header = QHBoxLayout()

        title = QLabel(Strings.get("label_sources"))
        title.setStyleSheet("font-weight: bold; font-size: 14px;")

        btn_box = QHBoxLayout()
        add_file_btn = QPushButton(Strings.get("btn_add_files"))
        add_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_file_btn.clicked.connect(self._open_file_dialog)

        add_dir_btn = QPushButton(Strings.get("btn_add_folder"))
        add_dir_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_dir_btn.clicked.connect(self._open_directory_dialog)

        btn_box.addWidget(add_file_btn)
        btn_box.addWidget(add_dir_btn)

        header.addWidget(title)
        header.addStretch()
        header.addLayout(btn_box)

        self.file_list = FileListWidget()
        self.file_list.model().rowsInserted.connect(self._update_convert_button_state)
        self.file_list.model().rowsRemoved.connect(self._update_convert_button_state)

        self.left_column.addLayout(header)
        self.left_column.addWidget(self.file_list, 1)

    def _setup_right_column(self):
        title = QLabel(Strings.get("label_settings"))
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 6px;")
        self.right_column.addWidget(title)

        # File types groups
        self.feature_widgets = {}
        self.type_checkboxes = {}
        self._build_file_type_settings()

        # Output path
        self.right_column.addSpacing(10)
        self._build_output_path_section()
        self._build_structure_section()
        self._build_output_overwrite()

        self.right_column.addStretch()

        # Convert button
        self.convert_btn = QPushButton(Strings.get("btn_convert"))
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet(Styles.CONVERT)
        self.convert_btn.clicked.connect(self._convert)
        self.right_column.addWidget(self.convert_btn)

    def _build_file_type_settings(self):
        for kind in consts.FILE_KINDS:
            # Group container
            group = QWidget()
            layout = QVBoxLayout(group)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Group toggle
            cb_type = QCheckBox(kind.title)
            cb_type.setStyleSheet(Styles.CHECKBOX)
            cb_type.setCursor(Qt.CursorShape.PointingHandCursor)
            cb_type.setChecked(True)

            self.type_checkboxes[kind.id] = cb_type

            # Sub options
            sub_options = QWidget()
            sub_layout = QVBoxLayout(sub_options)
            sub_layout.setContentsMargins(26, 4, 0, 8)
            sub_layout.setSpacing(2)

            # Models output format
            if kind.id == "models":
                self.fmt_combo = QComboBox()
                self.fmt_combo.setStyleSheet(Styles.COMBO)
                self.fmt_combo.setCursor(Qt.CursorShape.PointingHandCursor)
                self.fmt_combo.setItemDelegate(QStyledItemDelegate())
                self.fmt_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

                for fmt in consts.MODEL_FORMATS:
                    self.fmt_combo.addItem(str(fmt), fmt)

                self.fmt_combo.currentIndexChanged.connect(self._update_feature_availability)
                sub_layout.addWidget(self.fmt_combo)

            # Feature specific checkboxes
            for feat_id, feat_title in kind.feature_map.items():
                cb_feat = QCheckBox(feat_title)
                cb_feat.setStyleSheet(Styles.CHECKBOX)
                cb_feat.setCursor(Qt.CursorShape.PointingHandCursor)
                sub_layout.addWidget(cb_feat)
                self.feature_widgets[feat_id] = cb_feat

            cb_type.toggled.connect(sub_options.setEnabled)
            layout.addWidget(cb_type)

            # Suffixes hint
            suffix_hint = QLabel(", ".join(kind.suffixes))
            suffix_hint.setStyleSheet(Styles.HINT)

            layout.addWidget(suffix_hint)
            layout.addWidget(sub_options)
            self.right_column.addWidget(group)

    def _build_output_path_section(self):
        lbl = QLabel(Strings.get("label_output_path"))
        lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #abb2bf;")
        self.right_column.addWidget(lbl)

        self.mode_group = QButtonGroup(self)

        # Default output radio button
        self.radio_same_dir = QRadioButton(Strings.get("opt_output_default"))
        self.radio_same_dir.setStyleSheet(Styles.RADIO)
        self.radio_same_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_group.addButton(self.radio_same_dir)
        self.right_column.addWidget(self.radio_same_dir)

        # Custom output
        self.path_row_widget = QWidget()
        path_layout = QHBoxLayout(self.path_row_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(8)

        # Custom output radio button
        self.radio_custom_dir = QRadioButton("")
        self.radio_custom_dir.setStyleSheet(Styles.RADIO)
        self.radio_custom_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_custom_dir.setChecked(True)
        self.mode_group.addButton(self.radio_custom_dir)

        # Custom output path input
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(Strings.get("placeholder_path"))
        self.path_edit.setStyleSheet(Styles.INPUT)
        self.path_edit.setText(consts.DEFAULT_OUTPUT.as_posix())

        # Custom output path browse
        self.browse_btn = QPushButton("...")
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.setFixedHeight(30)
        self.browse_btn.clicked.connect(self._browse_output_path)

        # Autoselect radio button
        self.path_row_widget.mousePressEvent = lambda e: self.radio_custom_dir.setChecked(True)

        # Add to layout
        path_layout.addWidget(self.radio_custom_dir)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        self.right_column.addWidget(self.path_row_widget)

        # Sync state
        self.path_edit.textChanged.connect(self._handle_output_change)
        self.radio_same_dir.toggled.connect(self._handle_output_change)
        self.radio_custom_dir.toggled.connect(self._handle_output_change)

    def _build_structure_section(self):
        self.structure_container = QWidget()
        layout = QVBoxLayout(self.structure_container)
        layout.setContentsMargins(26, 0, 0, 0)
        layout.setSpacing(4)

        # Flat or structured output
        self.radio_tree = QRadioButton(Strings.get("opt_output_tree"))
        self.radio_tree.setStyleSheet(Styles.RADIO)
        self.radio_tree.setCursor(Qt.CursorShape.PointingHandCursor)

        self.radio_flat = QRadioButton(Strings.get("opt_output_flat"))
        self.radio_flat.setStyleSheet(Styles.RADIO)
        self.radio_flat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_tree.setChecked(True)

        s_group = QButtonGroup(self)
        s_group.addButton(self.radio_tree)
        s_group.addButton(self.radio_flat)

        # Add to layout
        layout.addWidget(self.radio_tree)
        layout.addWidget(self.radio_flat)

        self.right_column.addWidget(self.structure_container)

    def _build_output_overwrite(self):
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Checkbox
        self.cb_unique_names = QCheckBox(Strings.get("cb_unique_names"))
        self.cb_unique_names.setStyleSheet(Styles.CHECKBOX)
        self.cb_unique_names.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_unique_names.setChecked(False)

        # Hint
        overwrite_hint = QLabel(Strings.get("hint_unique_names"))
        overwrite_hint.setStyleSheet(Styles.HINT)

        # Add to layout
        layout.addWidget(self.cb_unique_names)
        layout.addWidget(overwrite_hint)

        self.right_column.addSpacing(10)
        self.right_column.addWidget(group)

    def _sync_output_ui(self):
        is_custom = self.radio_custom_dir.isChecked()
        self.path_edit.setEnabled(is_custom)
        self.browse_btn.setEnabled(is_custom)
        self.structure_container.setEnabled(is_custom)

    def _convert(self) -> None:
        allowed = self._get_activated_suffixes()
        fmt: consts.ModelFormat = self.fmt_combo.currentData()

        def predicate(path: Path) -> bool:
            return (path.suffix.lower() in allowed) or (path.name in consts.NBT_FILENAMES)

        options = UserOptions(
            model_formats=[fmt.id] if fmt else None,
            parse_skeleton=self.feature_widgets[FT.SKELETON.id].isChecked(),
            parse_animation=self.feature_widgets[FT.ANIMATION.id].isChecked(),
            overwrite=not self.cb_unique_names.isChecked(),
        )

        output = Path(self.path_edit.text()) if self.radio_custom_dir.isChecked() else None
        relative = self.radio_tree.isChecked()

        paths = [Path(self.file_list.item(i).data(Qt.ItemDataRole.UserRole)) for i in range(self.file_list.count())]

        self._thread = QThread()
        self._worker = ConvertWorker(paths, options, output, relative, predicate)

        def start_converting_thread():
            self._worker.moveToThread(self._thread)

            self._thread.started.connect(self._worker.run)
            self._worker.finished.connect(self._thread.quit)
            self._worker.finished.connect(lambda: self.convert_btn.setEnabled(True))

            self._thread.finished.connect(self._thread.deleteLater)
            self._worker.finished.connect(self._worker.deleteLater)

            self._thread.start()

        start_converting_thread()

    def _get_activated_suffixes(self) -> set[str]:
        suffixes = set()
        for ft in consts.FILE_KINDS:
            if self.type_checkboxes[ft.id].isChecked():
                suffixes.update(ft.suffixes)
        return suffixes

    def _is_output_valid(self) -> bool:
        if self.radio_same_dir.isChecked():
            return True

        path = self.path_edit.text().strip()
        return bool(path) and not Path(path).is_file()

    def _update_path_style(self):
        if not self.radio_custom_dir.isChecked():
            self.path_edit.setStyleSheet(Styles.INPUT)
            return

        border_color = "#555" if self._is_output_valid() else "#e06c75"
        self.path_edit.setStyleSheet(f"{Styles.INPUT} QLineEdit {{ border-color: {border_color}; }}")

    def _handle_output_change(self):
        self._sync_output_ui()
        self._update_path_style()
        self._update_convert_button_state()

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
        has_sources = self.file_list.count() > 0
        output_valid = self._is_output_valid()
        is_okay = has_sources and output_valid

        checks = {
            not has_sources: Strings.get("tooltip_no_sources"),
            not output_valid: Strings.get("tooltip_invalid_output"),
        }

        tooltip = checks.get(True, "")

        text = Strings.get("btn_convert")

        self.convert_btn.setText(text)
        self.convert_btn.setEnabled(is_okay)
        self.convert_btn.setToolTip(tooltip)
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)

    def _open_file_dialog(self):
        fs, _ = QFileDialog.getOpenFileNames(self, Strings.get("dialog_files"))
        if fs:
            self.file_list.add_sources(fs)

    def _open_directory_dialog(self):
        d = QFileDialog.getExistingDirectory(self, Strings.get("dialog_folder"))
        if d:
            self.file_list.add_sources([d])

    def _browse_output_path(self):
        d = QFileDialog.getExistingDirectory(self, Strings.get("dialog_output"))
        if d:
            self.path_edit.setText(d)
