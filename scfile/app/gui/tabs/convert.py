from pathlib import Path
from typing import override

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QCloseEvent, QKeyEvent, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from scfile.app import files
from scfile.app.consts import DEFAULT_OUTPUT
from scfile.app.enums import OutputLayout
from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.formats import FORMAT_GROUPS, model_formats
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.card import CardWidget
from scfile.app.gui.widgets.combo import ComboBox
from scfile.app.gui.widgets.conflict import ConflictWidget
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.path import PathInputWidget
from scfile.app.gui.widgets.progress import ProgressButton
from scfile.app.gui.widgets.sources import SourcesWidget
from scfile.app.gui.widgets.toggle import ToggleButton
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.gui.workers.counter import FileCounter
from scfile.app.tasks.convert import ConvertTask
from scfile.content import ModelContent
from scfile.content.models import Feature
from scfile.core import ModelEncoder
from scfile.enums import FileFormat
from scfile.formats import registry
from scfile.options import DEFAULT_TARGETS, Options


class FormatCard(QWidget):
    toggled = Signal(bool)

    def __init__(self, group, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._hovered = False
        self._target_hovered = False
        self._target: QWidget | None = None
        self.setObjectName("formatCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(Styles.FORMAT_CARD)

        self._rows = QVBoxLayout(self)
        self._rows.setContentsMargins(0, 0, 0, 0)
        self._rows.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        header = QWidget()
        header.setFixedHeight(58)
        self._rows.addWidget(header)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(12)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(Styles.CHECKBOX)
        self.checkbox.setFixedWidth(18)
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(self._checked_changed)
        layout.addWidget(self.checkbox)

        image = QLabel()
        image.setPixmap(
            QPixmap(str(files.resource(f"assets/formats.{group.name}.png"))).scaled(
                QSize(32, 32),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(image)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        title = QLabel(strings.get(group.label))
        title.setObjectName("formatCardTitle")
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content.addWidget(title)
        self._title = title

        hint = QLabel(" ".join(group.display))
        hint.setObjectName("formatCardHint")
        hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content.addWidget(hint)

        layout.addLayout(content, 1)
        self._layout = layout
        self.setMinimumHeight(58)
        self._sync_style()

    def add_details(self, widget: QWidget) -> None:
        self._rows.addWidget(widget)
        widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(58 + widget.sizeHint().height())

    def add_target(self, target: QWidget) -> None:
        self._layout.addWidget(target)
        self.checkbox.toggled.connect(target.setEnabled)
        if isinstance(target, ComboBox):
            self._target = target
            target.installEventFilter(self)

    @property
    def checked(self) -> bool:
        return self.checkbox.isChecked()

    def _checked_changed(self, checked: bool) -> None:
        self._sync_style()
        self.toggled.emit(checked)

    def _sync_style(self) -> None:
        self.setProperty("checked", self.checkbox.isChecked())
        for widget in (self, self.checkbox):
            widget.setProperty("hovered", self._hovered and not self._target_hovered)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    @override
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.isEnabled() and event.button() is Qt.MouseButton.LeftButton:
            self.checkbox.toggle()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    @override
    def enterEvent(self, event) -> None:
        self._hovered = True
        self._sync_style()
        super().enterEvent(event)

    @override
    def leaveEvent(self, event) -> None:
        self._hovered = False
        self._sync_style()
        super().leaveEvent(event)

    @override
    def eventFilter(self, watched, event) -> bool:
        if watched is self._target and event.type() in (QEvent.Type.Enter, QEvent.Type.Leave):
            self._target_hovered = event.type() is QEvent.Type.Enter and self._target and self._target.isEnabled()
            self._sync_style()
        return super().eventFilter(watched, event)


class ConvertForm(QWidget):
    changed = Signal()
    filters_changed = Signal()
    output_changed = Signal(object)
    submitted = Signal()

    def __init__(self, output: Path = DEFAULT_OUTPUT, parent: QWidget | None = None):
        super().__init__(parent)
        self.default_output = output
        self.groups: dict[str, QCheckBox] = {}
        self._build_ui(output)
        self._sync_output()

    @override
    def minimumSizeHint(self) -> QSize:
        size = super().minimumSizeHint()
        width = self.structure.layout().minimumSize().width()
        for layout in (self.output_card.content, self.output_card.layout(), self.layout()):
            margins = layout.contentsMargins()
            width += margins.left() + margins.right()
        size.setWidth(max(size.width(), width))
        return size

    @override
    def sizeHint(self) -> QSize:
        size = super().sizeHint()
        size.setWidth(max(size.width(), self.minimumSizeHint().width()))
        return size

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
        return Options(
            skeleton=self.skeleton.isEnabled() and self.skeleton.isChecked(),
            animation=self.animation.isEnabled() and self.animation.isChecked(),
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
        return OutputLayout.ROOTED if self.output_tree.isChecked() else OutputLayout.DUMP

    @property
    def output_valid(self) -> bool:
        if self.output_origin.isChecked():
            return True

        output = self.output
        return output is not None and not output.is_file()

    def set_count(self, text: str) -> None:
        if not self.submit.running:
            label = strings.get("button.convert")
            self.submit.setText(f"{label} ({text})" if text else label)

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
        layout.setSpacing(8)

        heading = QWidget()
        heading.setFixedHeight(28)
        heading_layout = QHBoxLayout(heading)
        heading_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel(strings.get("label.convert.settings"))
        title.setStyleSheet(Styles.TITLE)
        heading_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignVCenter)
        heading_layout.addStretch()
        layout.addWidget(heading)

        self._build_format_groups(layout)
        self._build_output(layout, output)

        self.conflict = ConflictWidget()
        conflict_card = CardWidget()
        conflict_card.content.addWidget(self.conflict)
        layout.addWidget(conflict_card)
        layout.addStretch()

        self.warnings = WarningsWidget()
        layout.addWidget(self.warnings)

        self.submit = ProgressButton(strings.get("button.convert"))
        self.submit.setMinimumHeight(54)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self.submitted.emit)
        layout.addWidget(self.submit)
        self.submit_cursor = DisabledCursor(self.submit)

    def _build_format_groups(self, layout: QVBoxLayout) -> None:
        self.model_format = ComboBox()
        self.model_format.setFixedWidth(76)
        self.model_format.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for fmt in model_formats():
            self.model_format.addItem(fmt.suffix, fmt)

        features = QWidget()
        feature_layout = QHBoxLayout(features)
        feature_layout.setContentsMargins(86, 0, 12, 9)
        feature_layout.setSpacing(8)
        self.skeleton = QCheckBox(strings.get("format.models.skeleton"))
        self.animation = QCheckBox(strings.get("format.models.animation"))
        for action in (self.skeleton, self.animation):
            action.setStyleSheet(Styles.CHECKBOX)
            action.setCursor(Qt.CursorShape.PointingHandCursor)
            action.setChecked(True)
            action.toggled.connect(lambda _: self.changed.emit())
            feature_layout.addWidget(action)
        feature_layout.addStretch()
        self.skeleton_cursor = DisabledCursor(self.skeleton)
        self.animation_cursor = DisabledCursor(self.animation)
        self.skeleton.toggled.connect(lambda enabled: self.animation.setChecked(False) if not enabled else None)
        self.animation.toggled.connect(lambda enabled: self.skeleton.setChecked(True) if enabled else None)
        self.model_format.currentIndexChanged.connect(self._sync_features)
        self._sync_features()

        for group in FORMAT_GROUPS:
            card = FormatCard(group)
            self.groups[group.name] = card.checkbox
            if group.name == "models":
                card.add_target(self.model_format)
                card.add_details(features)
                self.features_cursor = DisabledCursor(features)
                self.features_cursor.set(card.checkbox.isChecked())
                card.checkbox.toggled.connect(self.features_cursor.set)
            else:
                target = QLabel(DEFAULT_TARGETS[group.content_type].suffix)
                target.setObjectName("formatCardTarget")
                target.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                card.add_target(target)

            card.toggled.connect(lambda _: self.filters_changed.emit())
            layout.addWidget(card)

    def _sync_features(self) -> None:
        encoder = registry.encoders.get(self.selected_format)
        for feature, cursor in (
            (Feature.SKELETON, self.skeleton_cursor),
            (Feature.ANIMATION, self.animation_cursor),
        ):
            cursor.set(
                encoder is not None and issubclass(encoder, ModelEncoder) and encoder.supports(feature),
                strings.get("tooltip.convert.unsupported.feature"),
            )
        self.changed.emit()

    def _build_output(self, layout: QVBoxLayout, output: Path) -> None:
        card = CardWidget(strings.get("label.convert.output"))
        self.output_card = card
        content = card.content

        destination = QVBoxLayout()
        destination.setContentsMargins(0, 0, 0, 0)
        destination.setSpacing(4)
        content.addLayout(destination)

        modes = QButtonGroup(self)
        self.output_origin = QRadioButton(strings.get("option.convert.output.origin"))
        self.output_origin.setStyleSheet(Styles.RADIO)
        self.output_origin.setCursor(Qt.CursorShape.PointingHandCursor)
        modes.addButton(self.output_origin)
        destination.addWidget(self.output_origin)

        self.output_custom = QRadioButton(strings.get("option.convert.output.custom"))
        self.output_custom.setStyleSheet(Styles.RADIO)
        self.output_custom.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_custom.setChecked(True)
        modes.addButton(self.output_custom)
        destination.addWidget(self.output_custom)

        self.output_path = PathInputWidget(
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.convert.output"),
        )
        self.output_path.value = output.as_posix()

        path_row = QWidget()
        path_layout = QVBoxLayout(path_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(0)
        path_layout.addWidget(self.output_path)
        destination.addWidget(path_row)

        error_row = QWidget()
        error_layout = QVBoxLayout(error_row)
        error_layout.setContentsMargins(0, 0, 0, 0)
        error_layout.setSpacing(0)

        self.output_error = QLabel()
        self.output_error.setStyleSheet(Styles.ERROR)
        self.output_error.hide()
        error_layout.addWidget(self.output_error)
        content.addWidget(error_row)

        self.output_path.changed.connect(self._output_changed)
        self.output_path.activated.connect(self._select_custom_output)
        self.output_path.reset_requested.connect(self._restore_default_output)
        modes.buttonToggled.connect(self._output_changed)
        self._build_layout(content)
        layout.addWidget(card)

    def _build_layout(self, layout: QVBoxLayout) -> None:
        self.structure = QWidget()
        self.structure.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        section = QVBoxLayout(self.structure)
        section.setContentsMargins(0, 0, 0, 0)
        section.setSpacing(4)
        label = QLabel(strings.get("label.convert.output.layout"))
        label.setStyleSheet(Styles.LABEL)
        section.addWidget(label)
        toggle_group = QWidget()
        toggle_group.setObjectName("toggleGroup")
        toggle_group.setStyleSheet(Styles.TOGGLE_GROUP)
        toggle_group.setFixedHeight(32)
        structure = QHBoxLayout(toggle_group)
        structure.setContentsMargins(1, 1, 1, 1)
        structure.setSpacing(0)
        section.addWidget(toggle_group)

        self.output_tree = ToggleButton(strings.get("option.convert.output.tree"))
        self.output_dump = ToggleButton(strings.get("option.convert.output.dump"))

        modes = QButtonGroup(self)
        for button in (self.output_tree, self.output_dump):
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(Styles.TOGGLE_ITEM)
            button.setFixedHeight(30)
            modes.addButton(button)
            structure.addWidget(button, 1)
        self.output_tree.setChecked(True)

        modes.buttonToggled.connect(self._output_changed)
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
        self.structure.setVisible(custom)
        error = strings.get("tooltip.convert.invalid.output") if custom and not self.output_valid else ""
        self.output_path.invalid = bool(error)
        self.output_error.setText(error)
        self.output_error.setVisible(bool(error))


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

        self._sync_source_count()
        self._refresh()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(16)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedHeight(28)
        header = QHBoxLayout(header_widget)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel(strings.get("label.convert.sources"))
        title.setStyleSheet(Styles.TITLE)
        self.source_count = QLabel()
        self.source_count.setObjectName("sourceCount")
        self.source_count.setStyleSheet(Styles.COUNT_BADGE)
        self.source_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.source_count.hide()

        add_files = QPushButton(strings.get("button.convert.add.files"))
        add_files.setStyleSheet(Styles.BUTTON_UTILITY)
        add_files.setCursor(Qt.CursorShape.PointingHandCursor)
        add_files.clicked.connect(self._browse_files)

        add_folder = QPushButton(strings.get("button.convert.add.folder"))
        add_folder.setStyleSheet(Styles.BUTTON_UTILITY)
        add_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        add_folder.clicked.connect(self._browse_folder)

        header.addWidget(title, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.source_count, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addStretch()
        header.addWidget(add_files)
        header.addWidget(add_folder)

        self.sources = SourcesWidget()
        left.addWidget(header_widget)
        left.addSpacing(10)
        left.addWidget(self.sources, 1)

        self.form = ConvertForm(self.settings.export_path)
        layout.addLayout(left, stretch=2)
        layout.addWidget(self.form, stretch=1)

    def _sources_changed(self) -> None:
        self._sync_source_count()
        self._refresh()

    def _sync_source_count(self) -> None:
        count = self.sources.count()
        self.source_count.setText(str(count))
        self.source_count.setVisible(count > 0)

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
                (game_directory, strings.get("warning.convert.gamedir")),
                (output_within_sources, strings.get("warning.convert.overlap")),
            )
            if condition
        ]

    def _submit_error(self, sources: tuple[Path, ...]) -> str | None:
        errors = (
            "tooltip.task.busy" if self.tasks.busy else None,
            "tooltip.convert.invalid.sources" if not sources else None,
            "tooltip.convert.invalid.targets" if not (self.counter.busy or self.counter.count) else None,
            "tooltip.convert.invalid.output" if not self.form.output_valid else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        sources = tuple(Path(source) for source in self.sources.values)
        output = self.form.output

        self.form.set_count(self.counter.text if self.sources.values else "")
        self.form.set_warnings(self._warnings(sources, output))

        error = self._submit_error(sources)
        self.form.set_available(error is None, error or "")

    def _start_conversion(self) -> None:
        if self.running:
            self.tasks.cancel()
            return

        task = ConvertTask(
            workers=self.settings.workers,
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
        paths, _ = QFileDialog.getOpenFileNames(self, strings.get("dialog.convert.add.files"))
        if paths:
            self.sources.add_sources(paths)

    def _browse_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, strings.get("dialog.convert.add.folder"))
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
