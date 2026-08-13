from pathlib import Path
from typing import override

from PySide6.QtCore import Qt, Signal
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

from scfile.app.consts import DEFAULT_OUTPUT
from scfile.app.enums import OutputLayout
from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.formats import FORMAT_GROUPS, model_formats
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.conflict import ConflictWidget
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.path import PathInputWidget
from scfile.app.gui.widgets.progress import ProgressButton
from scfile.app.gui.widgets.sources import SourcesWidget
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.gui.workers.counter import FileCounter
from scfile.app.tasks.convert import ConvertTask
from scfile.core import ModelEncoder
from scfile.enums import FileFormat
from scfile.formats import registry
from scfile.options import Options
from scfile.structures.content import ModelContent
from scfile.structures.models import Feature


FEATURES = {
    Feature.SKELETON: ("🦴", "feature.skeleton"),
    Feature.ANIMATION: ("🌀", "feature.animation"),
}


def _format_title(fmt: FileFormat) -> str:
    encoder = registry.encoders.get(fmt)
    icons = " ".join(
        icon
        for feature, (icon, _) in FEATURES.items()
        if encoder is not None and issubclass(encoder, ModelEncoder) and encoder.supports(feature)
    )
    return f"{fmt.upper()} {icons}".strip()


class ConvertForm(QWidget):
    changed = Signal()
    filters_changed = Signal()
    output_changed = Signal(object)
    submitted = Signal()

    def __init__(self, output: Path = DEFAULT_OUTPUT, parent: QWidget | None = None):
        super().__init__(parent)
        self.default_output = output
        self.groups: dict[str, QCheckBox] = {}
        self.features: dict[Feature, QCheckBox] = {}
        self.feature_cursors: dict[Feature, DisabledCursor] = {}
        self._build_ui(output)
        self._sync_output()
        self._sync_features()

    @property
    def filters(self) -> tuple[str, ...]:
        selected = (
            suffix for group in FORMAT_GROUPS if self.groups[group.name].isChecked() for suffix in group.filters
        )
        return tuple(selected)

    @property
    def filtered(self) -> bool:
        return any(not self.groups[group.name].isChecked() for group in FORMAT_GROUPS)

    @property
    def options(self) -> Options:
        skeleton = self.features[Feature.SKELETON]
        animation = self.features[Feature.ANIMATION]
        return Options(
            model={
                "skeleton": skeleton.isEnabled() and skeleton.isChecked(),
                "animation": animation.isEnabled() and animation.isChecked(),
            },
            targets={ModelContent: self.selected_format},
            on_conflict=self.conflict.value,
        )

    @property
    def selected_format(self) -> FileFormat:
        return FileFormat(self.model_format.currentData())

    @property
    def output(self) -> Path | None:
        if self.output_origin.isChecked():
            return None

        value = self.output_path.value.strip()
        return Path(value) if value else None

    @property
    def output_layout(self) -> OutputLayout:
        return OutputLayout.ROOTED if self.output_tree.isChecked() else OutputLayout.FLAT

    @property
    def output_valid(self) -> bool:
        if self.output_origin.isChecked():
            return True

        output = self.output
        return output is not None and not output.is_file()

    def set_count(self, text: str) -> None:
        if not self.submit.running:
            self.submit.setText(f"{strings.get('button.convert')} ({text})")

    def set_available(self, available: bool, tooltip: str = "") -> None:
        self.submit_cursor.set(self.submit.running or available, strings.get(tooltip))

    def set_warnings(self, warnings: list[str]) -> None:
        self.warnings.set_messages(warnings)

    def start(self, total: int = 0) -> None:
        self.submit.start(total)
        self.submit_cursor.set(True)

    def advance(self) -> None:
        self.submit.advance()

    def finish(self) -> None:
        self.submit.finish()

    def _build_ui(self, output: Path) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(strings.get("label.settings"))
        title.setStyleSheet(Styles.TITLE)
        layout.addWidget(title)
        layout.addSpacing(10)

        self._build_format_groups(layout)
        layout.addSpacing(10)
        self._build_output(layout, output)
        self._build_layout(layout)
        layout.addSpacing(20)

        self.conflict = ConflictWidget()
        layout.addWidget(self.conflict)
        layout.addStretch()

        self.warnings = WarningsWidget()
        layout.addWidget(self.warnings)

        self.submit = ProgressButton(strings.get("button.convert"))
        self.submit.setMinimumHeight(50)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self.submitted.emit)
        layout.addWidget(self.submit)
        self.submit_cursor = DisabledCursor(self.submit)

    def _build_format_groups(self, layout: QVBoxLayout) -> None:
        self.model_format = QComboBox()
        self.model_format.setStyleSheet(Styles.COMBO)
        self.model_format.setCursor(Qt.CursorShape.PointingHandCursor)
        self.model_format.setItemDelegate(QStyledItemDelegate())
        self.model_format.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for fmt in model_formats():
            self.model_format.addItem(_format_title(fmt), fmt)
        self.model_format.currentIndexChanged.connect(self._sync_features)

        for group in FORMAT_GROUPS:
            widget = QWidget()
            group_layout = QVBoxLayout(widget)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(0)

            toggle = QCheckBox(f"{group.icon} {strings.get(group.label)}")
            toggle.setStyleSheet(Styles.CHECKBOX)
            toggle.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle.setChecked(True)
            self.groups[group.name] = toggle

            options = QWidget()
            options_layout = QVBoxLayout(options)
            options_layout.setContentsMargins(26, 4, 0, 8)
            options_layout.setSpacing(2)

            if group.name == "models":
                options_layout.addWidget(self.model_format)

            for feature in group.features:
                icon, label = FEATURES[feature]
                checkbox = QCheckBox(f"{icon} {strings.get(label)}")
                checkbox.setStyleSheet(Styles.CHECKBOX)
                checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
                options_layout.addWidget(checkbox)
                self.features[feature] = checkbox
                self.feature_cursors[feature] = DisabledCursor(checkbox)

            suffixes = QLabel(", ".join(group.display))
            suffixes.setStyleSheet(f"{Styles.HINT}; margin-left: 24px;")

            toggle.toggled.connect(options.setEnabled)
            toggle.toggled.connect(lambda _: self.filters_changed.emit())
            group_layout.addWidget(toggle)
            group_layout.addWidget(suffixes)
            group_layout.addWidget(options)
            layout.addWidget(widget)

        self.features[Feature.SKELETON].toggled.connect(self._skeleton_changed)
        self.features[Feature.ANIMATION].toggled.connect(self._animation_changed)

    def _build_output(self, layout: QVBoxLayout, output: Path) -> None:
        label = QLabel(strings.get("label.output"))
        label.setStyleSheet(Styles.LABEL)
        layout.addWidget(label)

        modes = QButtonGroup(self)
        self.output_origin = QRadioButton(strings.get("option.output.origin"))
        self.output_origin.setStyleSheet(Styles.RADIO)
        self.output_origin.setCursor(Qt.CursorShape.PointingHandCursor)
        modes.addButton(self.output_origin)
        layout.addWidget(self.output_origin)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        self.output_custom = QRadioButton()
        self.output_custom.setStyleSheet(Styles.RADIO)
        self.output_custom.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_custom.setChecked(True)
        modes.addButton(self.output_custom)

        self.output_path = PathInputWidget(
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.output"),
        )
        self.output_path.value = output.as_posix()

        row_layout.addWidget(self.output_custom)
        row_layout.addWidget(self.output_path)
        layout.addWidget(row)

        error_row = QWidget()
        error_layout = QVBoxLayout(error_row)
        error_layout.setContentsMargins(25, 0, 0, 0)
        error_layout.setSpacing(0)

        self.output_error = QLabel()
        self.output_error.setStyleSheet(Styles.ERROR)
        self.output_error.hide()
        error_layout.addWidget(self.output_error)
        layout.addWidget(error_row)

        self.output_path.changed.connect(self._output_changed)
        self.output_path.activated.connect(self._select_custom_output)
        self.output_path.clear_requested.connect(self._restore_default_output)
        modes.buttonToggled.connect(self._output_changed)

    def _build_layout(self, layout: QVBoxLayout) -> None:
        self.structure = QWidget()
        structure = QVBoxLayout(self.structure)
        structure.setContentsMargins(25, 0, 0, 0)
        structure.setSpacing(5)

        self.output_tree = QRadioButton(strings.get("option.output.tree"))
        self.output_tree.setStyleSheet(Styles.RADIO)
        self.output_tree.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_tree.setChecked(True)

        self.output_flat = QRadioButton(strings.get("option.output.flat"))
        self.output_flat.setStyleSheet(Styles.RADIO)
        self.output_flat.setCursor(Qt.CursorShape.PointingHandCursor)

        modes = QButtonGroup(self)
        modes.addButton(self.output_tree)
        modes.addButton(self.output_flat)

        structure.addWidget(self.output_tree)
        structure.addWidget(self.output_flat)
        layout.addWidget(self.structure)

    def _output_changed(self, *_: object) -> None:
        self._sync_output()
        self.output_changed.emit(self.output)
        self.changed.emit()

    def _select_custom_output(self) -> None:
        if not self.output_custom.isChecked():
            self.output_custom.setChecked(True)

    def _restore_default_output(self) -> None:
        self.output_path.value = self.default_output.as_posix()
        self._output_changed()

    def set_default_output(self, output: Path) -> None:
        self.default_output = output
        self.output_path.value = output.as_posix()
        self._output_changed()

    def _sync_output(self) -> None:
        custom = self.output_custom.isChecked()
        self.output_path.read_only = not custom
        self.structure.setEnabled(custom)
        error = strings.get("tooltip.invalid.output") if custom and not self.output_valid else ""
        self.output_path.invalid = bool(error)
        self.output_error.setText(error)
        self.output_error.setVisible(bool(error))

    def _sync_features(self) -> None:
        encoder = registry.encoders.get(self.selected_format)
        for feature, widget in self.features.items():
            supported = encoder is not None and issubclass(encoder, ModelEncoder) and encoder.supports(feature)
            self.feature_cursors[feature].set(supported)
            widget.setChecked(supported)

    def _skeleton_changed(self, enabled: bool) -> None:
        if not enabled:
            self.features[Feature.ANIMATION].setChecked(False)

    def _animation_changed(self, enabled: bool) -> None:
        if enabled:
            self.features[Feature.SKELETON].setChecked(True)


class ConvertTab(QWidget):
    error = Signal(object)
    settings_changed = Signal()

    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self.counter = FileCounter(self)
        self.running = False
        self._build_ui()

        self.sources.changed.connect(self._sources_changed)
        self.form.changed.connect(self._sync)
        self.form.filters_changed.connect(self._filters_changed)
        self.form.submitted.connect(self._start_conversion)
        self.counter.changed.connect(self._sync)
        self.counter.error.connect(self.error.emit)
        self.tasks.reported.connect(self._report)
        self.tasks.completed.connect(self._complete)
        self.tasks.busy_changed.connect(self._sync)

        self._refresh()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        left = QVBoxLayout()
        header = QHBoxLayout()

        title = QLabel(strings.get("label.sources"))
        title.setStyleSheet(Styles.TITLE)

        add_files = QPushButton(strings.get("button.add_files"))
        add_files.setStyleSheet(Styles.BUTTON)
        add_files.setCursor(Qt.CursorShape.PointingHandCursor)
        add_files.clicked.connect(self._browse_files)

        add_folder = QPushButton(strings.get("button.add_folder"))
        add_folder.setStyleSheet(Styles.BUTTON)
        add_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        add_folder.clicked.connect(self._browse_folder)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_files)
        header.addWidget(add_folder)

        self.sources = SourcesWidget()
        left.addLayout(header)
        left.addWidget(self.sources, 1)

        self.form = ConvertForm(self.settings.export_path)
        layout.addLayout(left, stretch=2)
        layout.addWidget(self.form, stretch=1)

    def _sources_changed(self) -> None:
        self._refresh()

    def _filters_changed(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        self.counter.refresh(self.sources.values, self.form.filters)

    def _warnings(self, sources: tuple[Path, ...], output: Path | None) -> list[str]:
        targets = (output,) if output is not None else (sources if self.form.output_origin.isChecked() else ())
        game_root = self.settings.game_root
        game_directory = game_root is not None and any(path.resolve().is_relative_to(game_root) for path in targets)
        game_directory = game_directory or any("modassets/assets" in path.as_posix().lower() for path in targets)
        game_directory = game_directory or (output is None and self.counter.game_assets)
        output_within_sources = output is not None and any(output.is_relative_to(source) for source in sources)

        return [
            message
            for condition, message in (
                (game_directory, strings.get("warning.gamedir")),
                (output_within_sources, strings.get("warning.output_overlap")),
            )
            if condition
        ]

    def _submit_error(self, sources: tuple[Path, ...]) -> str | None:
        errors = (
            "tooltip.task.busy" if self.tasks.busy else None,
            "tooltip.invalid.sources" if not sources else None,
            "tooltip.invalid.targets" if not (self.counter.busy or self.counter.count) else None,
            "tooltip.invalid.output" if not self.form.output_valid else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        sources = tuple(Path(source) for source in self.sources.values)
        output = self.form.output

        self.form.set_count(self.counter.text)
        self.form.set_warnings(self._warnings(sources, output))

        error = self._submit_error(sources)
        self.form.set_available(error is None, error or "")

    def _start_conversion(self) -> None:
        if self.running:
            self.tasks.cancel()
            return

        task = ConvertTask(
            sources=self.sources.values,
            filters=self.form.filters,
            options=self.form.options,
            output=self.form.output,
            layout=self.form.output_layout,
            total=None if self.counter.busy else self.counter.count,
            filtered=self.form.filtered,
        )
        self.running = self.tasks.start(task)
        if self.running:
            self.form.start()
            self.form.submit_cursor.set(True)
        self._sync()

    def _report(self, event: object) -> None:
        if not self.running:
            return

        match event:
            case TaskStarted():
                self.form.start(event.total)
            case TaskItem() | TaskItemFailure():
                self.form.advance()

    def _complete(self, summary: object) -> None:
        if self.running and isinstance(summary, TaskSummary):
            self.running = False
            self.form.finish()
            self._sync()

    def apply_export_path(self, path: Path) -> None:
        self.form.set_default_output(path)
        self._sync()

    def stop(self) -> None:
        self.counter.stop()

    def _browse_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, strings.get("dialog.add_files"))
        if paths:
            self.sources.add_sources(paths)

    def _browse_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, strings.get("dialog.add_folder"))
        if path:
            self.sources.add_sources((path,))

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_F5:
            self._refresh()
        super().keyPressEvent(event)

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        self.stop()
        super().closeEvent(event)
