from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent, QKeyEvent
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

from scfile.core import Options
from scfile.core.options import ON_CONFLICT_OPTIONS
from scfile.gui import workers
from scfile.gui.shared import consts, strings
from scfile.gui.shared.consts import FT
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets import PathInputWidget, SourcesWidget, WarningsWidget
from scfile.gui.workers.convert import ConvertContext, ConvertWorker
from scfile.gui.workers.counter import CounterWorker


class ConverterTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_counter()
        self._setup_warnings()
        self._setup_converter()
        self._build_ui()

    def _setup_counter(self):
        self._counter = CounterWorker()
        self._counter.changed.connect(self._handle_counter)

    def _setup_warnings(self):
        self._warnings = WarningsWidget()
        self._warnings.add_rule(self._warn_gamedir)
        self._warnings.add_rule(self._warn_collision)

    def _setup_converter(self):
        self._converter: ConvertWorker | None = None
        self._converter_thread: QThread | None = None

    def _warn_gamedir(self) -> str | None:
        custom = self.output_to_custom.isChecked()
        origin = self.output_to_origin.isChecked()
        output = Path(self.output_path.text().strip())
        sources = [Path(s) for s in self._get_sources()]
        targets = [output] if (custom and output) else sources

        if any("modassets/assets" in path.as_posix() for path in targets):
            return strings.get("warning.gamedir")
        if origin and self._counter.gamedir:
            return strings.get("warning.gamedir")

    def _warn_collision(self) -> str | None:
        custom = self.output_to_custom.isChecked()
        output = Path(self.output_path.text().strip())

        if custom and output:
            for source in (Path(s) for s in self._get_sources()):
                if output == source or output.is_relative_to(source):
                    return strings.get("warning.output_overlap")

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Create columns
        self.left = QVBoxLayout()
        self.right = QVBoxLayout()
        self._build_left()
        self._build_right()

        layout.addLayout(self.left, stretch=2)
        layout.addLayout(self.right, stretch=1)

        # Update UI state
        self._sync_output_widgets()
        self._sync_feature_widgets()
        self._sync_counter()

    def _build_left(self):
        header = QHBoxLayout()

        title = QLabel(strings.get("label.sources"))
        title.setStyleSheet(Styles.TITLE)

        add_file = QPushButton(strings.get("button.add_files"))
        add_file.setCursor(Qt.CursorShape.PointingHandCursor)
        add_file.clicked.connect(self._browse_files)

        add_dir = QPushButton(strings.get("button.add_folder"))
        add_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        add_dir.clicked.connect(self._browse_folder)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_file)
        header.addWidget(add_dir)

        self.sources = SourcesWidget()
        self.sources.changed.connect(self._handle_sources)

        self.left.addLayout(header)
        self.left.addWidget(self.sources, 1)

    def _build_right(self):
        title = QLabel(strings.get("label.settings"))
        title.setStyleSheet(Styles.TITLE)
        self.right.addWidget(title)
        self.right.addSpacing(10)

        # File types groups
        self.feat_checks: dict[str, QCheckBox] = {}
        self.kind_checks: dict[str, QCheckBox] = {}
        self._build_format()
        self._build_file_types()
        self.right.addSpacing(10)

        # Output path
        self._build_output()
        self._build_structure()
        self.right.addSpacing(10)

        # Output conflicts
        self._build_onconflict()
        self.right.addStretch()

        # Warnings
        self.right.addWidget(self._warnings)

        # Convert button
        self.convert = QPushButton(strings.get("button.convert"))
        self.convert.setMinimumHeight(50)
        self.convert.setStyleSheet(Styles.BUTTON)
        self.convert.clicked.connect(self._convert)
        self.right.addWidget(self.convert)

    def _build_format(self):
        self.format = QComboBox()
        self.format.setStyleSheet(Styles.COMBO)
        self.format.setCursor(Qt.CursorShape.PointingHandCursor)
        self.format.setItemDelegate(QStyledItemDelegate())
        self.format.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        for fmt in consts.MODEL_FORMATS:
            self.format.addItem(str(fmt), fmt)

        self.format.currentIndexChanged.connect(self._handle_formats)

    def _build_file_types(self):
        for kind in consts.FILE_KINDS:
            group = QWidget()
            layout = QVBoxLayout(group)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Group toggle
            toggle = QCheckBox(kind.title)
            toggle.setStyleSheet(Styles.CHECKBOX)
            toggle.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle.setChecked(True)
            toggle.toggled.connect(self._handle_kinds)
            self.kind_checks[kind.id] = toggle

            # Sub options
            options = QWidget()
            options_layout = QVBoxLayout(options)
            options_layout.setContentsMargins(26, 4, 0, 8)
            options_layout.setSpacing(2)

            # Models output format
            if kind.id == "models":
                options_layout.addWidget(self.format)

            # Feature specific checkboxes
            for feat_id, feat_title in kind.feature_map.items():
                cb_feat = QCheckBox(feat_title)
                cb_feat.setStyleSheet(Styles.CHECKBOX)
                cb_feat.setCursor(Qt.CursorShape.PointingHandCursor)
                options_layout.addWidget(cb_feat)
                self.feat_checks[feat_id] = cb_feat

            toggle.toggled.connect(options.setEnabled)

            # Suffixes hint
            suffixes = QLabel(", ".join(kind.suffixes))
            suffixes.setStyleSheet(f"{Styles.HINT}; margin-left: 24px;")

            layout.addWidget(toggle)
            layout.addWidget(suffixes)
            layout.addWidget(options)
            self.right.addWidget(group)

    def _build_output(self):
        label = QLabel(strings.get("label.output"))
        label.setStyleSheet(Styles.LABEL)
        self.right.addWidget(label)

        self.output_mode = QButtonGroup(self)

        # Default output radio button
        self.output_to_origin = QRadioButton(strings.get("option.output.origin"))
        self.output_to_origin.setStyleSheet(Styles.RADIO)
        self.output_to_origin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_mode.addButton(self.output_to_origin)
        self.right.addWidget(self.output_to_origin)

        # Custom output
        output_row = QWidget()
        path_layout = QHBoxLayout(output_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(0)

        # Custom output radio button
        self.output_to_custom = QRadioButton("")
        self.output_to_custom.setStyleSheet(Styles.RADIO)
        self.output_to_custom.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_to_custom.setChecked(True)
        self.output_mode.addButton(self.output_to_custom)

        # Custom output path input
        self.output_path = PathInputWidget(
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.output"),
        )
        self.output_path.setText(consts.DEFAULT_OUTPUT.as_posix())

        # Autoselect radio button
        output_row.mousePressEvent = lambda e: self.output_to_custom.setChecked(True)

        # Add to layout
        path_layout.addWidget(self.output_to_custom)
        path_layout.addWidget(self.output_path)
        self.right.addWidget(output_row)

        # Sync state
        self.output_path.textChanged.connect(self._handle_output)
        self.output_mode.buttonToggled.connect(self._handle_output)
        self.output_to_origin.toggled.connect(self._handle_output)
        self.output_to_custom.toggled.connect(self._handle_output)

    def _build_structure(self):
        self.structure = QWidget()
        layout = QVBoxLayout(self.structure)
        layout.setContentsMargins(25, 0, 0, 0)
        layout.setSpacing(5)

        # Flat or structured output
        self.output_tree = QRadioButton(strings.get("option.output.tree"))
        self.output_tree.setStyleSheet(Styles.RADIO)
        self.output_tree.setCursor(Qt.CursorShape.PointingHandCursor)

        self.output_flat = QRadioButton(strings.get("option.output.flat"))
        self.output_flat.setStyleSheet(Styles.RADIO)
        self.output_flat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_tree.setChecked(True)

        group = QButtonGroup(self)
        group.addButton(self.output_tree)
        group.addButton(self.output_flat)

        # Add to layout
        layout.addWidget(self.output_tree)
        layout.addWidget(self.output_flat)

        self.right.addWidget(self.structure)

    def _build_onconflict(self):
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(strings.get("label.onconflict"))
        label.setStyleSheet(Styles.LABEL)
        layout.addWidget(label)

        toggle_group = QWidget()
        toggle_layout = QHBoxLayout(toggle_group)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)

        self.on_conflict = QButtonGroup(self)
        self.on_conflict.setExclusive(True)

        for option in ON_CONFLICT_OPTIONS:
            btn = QPushButton(strings.get(f"option.onconflict.{option}"))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("conflict_option", option)
            btn.setStyleSheet(Styles.TOGGLE_ITEM)
            self.on_conflict.addButton(btn)
            toggle_layout.addWidget(btn)

        self.on_conflict.buttons()[0].setChecked(True)
        toggle_group.setStyleSheet(Styles.TOGGLE_GROUP)

        hint = QLabel(strings.get("hint.onconflict"))
        hint.setStyleSheet(Styles.HINT)

        layout.addWidget(toggle_group)
        layout.addWidget(hint)

        self.right.addSpacing(10)
        self.right.addWidget(group)

    def _handle_sources(self):
        self._sync_counter()
        self._sync_button()
        self._sync_warnings()

    def _handle_kinds(self):
        self._sync_counter()

    def _handle_output(self):
        self._sync_output_widgets()
        self._sync_button()
        self._sync_warnings()

    def _handle_formats(self):
        self._sync_feature_widgets()

    def _handle_counter(self, text: str, count: int, busy: bool):
        label = strings.get("button.convert")
        self.convert.setText(f"{label} ({text})")
        self._sync_button()
        self._sync_warnings()

    def _sync_counter(self):
        self._counter.refresh(
            sources=self._get_sources(),
            whitelist=self._get_suffixes(),
        )

    def _sync_button(self):
        has_sources = self.sources.count() > 0
        has_targets = self._counter.busy or self._counter.count > 0
        output_valid = self._get_output_valid()
        ok = has_sources and has_targets and output_valid

        tooltip = {
            output_valid: "tooltip.invalid.output",
            has_targets: "tooltip.invalid.targets",
            has_sources: "tooltip.invalid.sources",
        }.get(False, "")

        self.convert.setEnabled(ok)
        self.convert.setToolTip(strings.get(tooltip))
        self.convert.setCursor(Qt.CursorShape.PointingHandCursor if ok else Qt.CursorShape.ForbiddenCursor)

    def _sync_warnings(self):
        self._warnings.update_state()

    def _sync_output_widgets(self):
        custom = self.output_to_custom.isChecked()
        self.output_path.setEnabled(custom)
        self.structure.setEnabled(custom)

    def _sync_feature_widgets(self):
        if fmt := self.format.currentData():
            for fid, w in self.feat_checks.items():
                ok = any(f.id == fid for f in fmt.features)
                w.setEnabled(ok)
                w.setChecked(ok)

    def _get_sources(self) -> list[str]:
        return [self.sources.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.sources.count())]

    def _get_suffixes(self) -> set[str]:
        suffixes: set[str] = set()
        for ft in consts.FILE_KINDS:
            if self.kind_checks[ft.id].isChecked():
                suffixes.update(ft.suffixes)
        return suffixes

    def _get_output_valid(self) -> bool:
        if self.output_to_origin.isChecked():
            return True
        path = self.output_path.text().strip()
        return bool(path) and not Path(path).is_file()

    def _convert(self):
        fmt: consts.ModelFormat = self.format.currentData()

        ft_skeleton = self.feat_checks[FT.SKELETON.id]
        ft_animation = self.feat_checks[FT.ANIMATION.id]

        on_conflict = self.on_conflict.checkedButton()

        context = ConvertContext(
            whitelist=self._get_suffixes(),
            options=Options(
                model_formats=[fmt.id] if fmt else None,
                skeleton=ft_skeleton.isEnabled() and ft_skeleton.isChecked(),
                animation=ft_animation.isEnabled() and ft_animation.isChecked(),
                on_conflict=on_conflict.property("conflict_option") if on_conflict else "overwrite",
            ),
            output=(Path(self.output_path.text()) if self.output_to_custom.isChecked() else None),
            relative=self.output_tree.isChecked(),
        )

        self._converter = ConvertWorker(sources=self._get_sources(), context=context)
        self._converter_thread = workers.execute(self._converter, on_done=self._on_convert_finish)
        self.convert.setEnabled(False)

    def _on_convert_finish(self):
        self._converter = None
        self._converter_thread = None
        self.convert.setEnabled(True)

    def _browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, strings.get("dialog.add_files"))
        if files:
            self.sources.add_sources(files)
            self._handle_sources()

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, strings.get("dialog.add_folder"))
        if path:
            self.sources.add_sources([path])
            self._handle_sources()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F5:
            self._handle_sources()
        super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent):
        self._counter.stop()

        if self._converter:
            self._converter.stop()

        super().closeEvent(event)
