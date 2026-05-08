from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from scfile.core.context.options import UserOptions
from scfile.gui import workers
from scfile.gui.shared import consts
from scfile.gui.shared.consts import FT
from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets import FileListWidget
from scfile.gui.widgets.path_input import PathInputWidget
from scfile.gui.widgets.warnings import WarningsWidget
from scfile.gui.workers.convert import ConvertContext, ConvertDispatcher
from scfile.gui.workers.counter import CountController


class ConverterTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_counter()
        self._setup_warning()
        self._setup_ui()
        self._refresh_count()

    def _setup_counter(self):
        # Create counter controller
        self.count_controller = CountController()
        self.count_controller.changed.connect(self._on_count_changed)

    def _on_count_changed(self, text: str, count: int, is_counting: bool):
        base_text = Strings.get("btn_convert")
        self.convert_btn.setText(f"{base_text} ({text})")
        self._sync_state()

    def _refresh_count(self):
        allowed = tuple(self._get_activated_suffixes())

        self.count_controller.refresh(
            sources=self._get_current_sources(),
            predicate=lambda path: path.lower().endswith(allowed),
        )

    def _setup_warning(self):
        self.warnings = WarningsWidget()

        def check_game_dir():
            custom = self.radio_custom_dir.isChecked()
            samedir = self.radio_same_dir.isChecked()
            output = Path(self.output_path.text().strip())
            sources = [Path(s) for s in self._get_current_sources()]
            targets = [output] if (custom and output) else sources

            gamedir_in_targets = any(["modassets/assets" in path.as_posix() for path in targets])

            if gamedir_in_targets or (samedir and self.count_controller.gamedir):
                return Strings.get("warn_game_dir")

        def check_collision():
            custom = self.radio_custom_dir.isChecked()
            output = Path(self.output_path.text().strip())
            if custom and output:
                sources = [Path(s) for s in self._get_current_sources()]
                for source in sources:
                    if output == source or output.is_relative_to(source):
                        return Strings.get("warn_path_collision")

        self.warnings.add_rule(check_game_dir)
        self.warnings.add_rule(check_collision)

    def _setup_ui(self):
        self.main_content_layout = QHBoxLayout(self)
        self.main_content_layout.setContentsMargins(10, 5, 10, 5)

        # Create columns
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        self._setup_left_column()
        self._setup_right_column()

        self.main_content_layout.addLayout(self.left_column, stretch=2)
        self.main_content_layout.addLayout(self.right_column, stretch=1)

        # Update state
        self._sync_output_ui()
        self._sync_state()
        self._sync_feature_availability()

    def _setup_left_column(self):
        header = QHBoxLayout()

        title = QLabel(Strings.get("label_sources"))
        title.setStyleSheet(Styles.TITLE)

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
        self.file_list.model().rowsInserted.connect(self._sync_state)
        self.file_list.model().rowsRemoved.connect(self._sync_state)

        self.file_list.model().rowsInserted.connect(self._refresh_count)
        self.file_list.model().rowsRemoved.connect(self._refresh_count)

        self.left_column.addLayout(header)
        self.left_column.addWidget(self.file_list, 1)

    def _setup_right_column(self):
        title = QLabel(Strings.get("label_settings"))
        title.setStyleSheet(f"{Styles.TITLE} margin-bottom: 6px;")
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

        # Warnings
        self.right_column.addWidget(self.warnings)

        # Convert button
        self.convert_btn = QPushButton(Strings.get("btn_convert"))
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet(Styles.BUTTON)
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
            cb_type.toggled.connect(self._refresh_count)

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

                self.fmt_combo.currentIndexChanged.connect(self._sync_feature_availability)
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
        lbl.setStyleSheet(Styles.LABEL)
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
        path_layout.setSpacing(0)

        # Custom output radio button
        self.radio_custom_dir = QRadioButton("")
        self.radio_custom_dir.setStyleSheet(Styles.RADIO)
        self.radio_custom_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_custom_dir.setChecked(True)
        self.mode_group.addButton(self.radio_custom_dir)

        # Custom output path input
        self.output_path = PathInputWidget(
            placeholder=Strings.get("placeholder_path"),
            caption=Strings.get("dialog_output"),
        )
        self.output_path.setText(consts.DEFAULT_OUTPUT.as_posix())

        # Autoselect radio button
        self.path_row_widget.mousePressEvent = lambda e: self.radio_custom_dir.setChecked(True)

        # Add to layout
        path_layout.addWidget(self.radio_custom_dir)
        path_layout.addWidget(self.output_path)
        self.right_column.addWidget(self.path_row_widget)

        # Sync state
        self.output_path.textChanged.connect(self._handle_output_change)
        self.radio_same_dir.toggled.connect(self._handle_output_change)
        self.radio_custom_dir.toggled.connect(self._handle_output_change)

    def _build_structure_section(self):
        self.structure_container = QWidget()
        layout = QVBoxLayout(self.structure_container)
        layout.setContentsMargins(25, 0, 0, 0)
        layout.setSpacing(5)

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
        self.output_path.setEnabled(is_custom)
        self.structure_container.setEnabled(is_custom)

    def _convert(self) -> None:
        allowed = self._get_activated_suffixes()
        fmt: consts.ModelFormat = self.fmt_combo.currentData()

        context = ConvertContext(
            options=UserOptions(
                model_formats=[fmt.id] if fmt else None,
                parse_skeleton=self.feature_widgets[FT.SKELETON.id].isChecked(),
                parse_animation=self.feature_widgets[FT.ANIMATION.id].isChecked(),
                overwrite=not self.cb_unique_names.isChecked(),
            ),
            output=Path(self.output_path.text()) if self.radio_custom_dir.isChecked() else None,
            relative=self.radio_tree.isChecked(),
            predicate=lambda path: (path.suffix.lower() in allowed) or (path.name in consts.NBT_FILENAMES),
        )

        paths = [Path(s) for s in self._get_current_sources()]

        self._convert_dispatcher = ConvertDispatcher(paths, context)
        self._convert_thread = workers.execute(
            self._convert_dispatcher,
            on_done=lambda: self.convert_btn.setEnabled(True),
        )

        self.convert_btn.setEnabled(False)

    def _get_activated_suffixes(self) -> set[str]:
        suffixes = set()
        for ft in consts.FILE_KINDS:
            if self.type_checkboxes[ft.id].isChecked():
                suffixes.update(ft.suffixes)
        return suffixes

    def _get_current_sources(self) -> list[str]:
        return [self.file_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.file_list.count())]

    def _is_output_valid(self) -> bool:
        if self.radio_same_dir.isChecked():
            return True

        path = self.output_path.text().strip()
        return bool(path) and not Path(path).is_file()

    def _handle_output_change(self):
        self._sync_output_ui()
        self._sync_state()

    def _sync_feature_availability(self):
        fmt = self.fmt_combo.currentData()
        if not fmt:
            return

        for fid, widget in self.feature_widgets.items():
            is_supported = any(f.id == fid for f in fmt.features)

            widget.setEnabled(is_supported)
            widget.setChecked(is_supported)

    def _sync_convert_button(self):
        has_sources = self.file_list.count() > 0
        has_targets = self.count_controller.is_counting or self.count_controller.count > 0
        output_valid = self._is_output_valid()
        is_okay = has_sources and has_targets and output_valid

        checks = {
            has_targets: Strings.get("tooltip_no_targets"),
            has_sources: Strings.get("tooltip_no_sources"),
            output_valid: Strings.get("tooltip_invalid_output"),
        }

        tooltip = checks.get(False, "")

        self.convert_btn.setEnabled(is_okay)
        self.convert_btn.setToolTip(tooltip)
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)

    def _sync_state(self):
        self.warnings.update_state()
        self._sync_convert_button()

    def _open_file_dialog(self):
        fs, _ = QFileDialog.getOpenFileNames(self, Strings.get("dialog_files"))
        if fs:
            self.file_list.add_sources(fs)

    def _open_directory_dialog(self):
        d = QFileDialog.getExistingDirectory(self, Strings.get("dialog_folder"))
        if d:
            self.file_list.add_sources([d])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F5:
            self._refresh_count()

        super().keyPressEvent(event)
