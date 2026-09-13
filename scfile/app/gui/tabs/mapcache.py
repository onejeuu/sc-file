from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.game import GameRoot, McWorld
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import MAX_FORM_WIDTH, Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.card import CalloutWidget, CardWidget
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathField
from scfile.app.gui.widgets.progress import ProgressButton
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.gui.workers.mapcache import MapCacheScanner
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.options import Options

class MapCacheTab(QWidget):
    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self.scanner = MapCacheScanner(self)
        self.touched: set[PathField] = set()
        self.world: McWorld | None = None
        self.running = False
        self._build_ui()

        self.tasks.busy_changed.connect(self._sync)
        self.tasks.reported.connect(self._report)
        self.tasks.completed.connect(self._complete)
        self.scanner.changed.connect(self._sync)
        self._source_changed(self.source.value)
        self._sync()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(16)

        heading = QHBoxLayout()
        title = QLabel(strings.get("title.mapcache"))
        title.setStyleSheet(Styles.TITLE)
        heading.addWidget(title, 0, Qt.AlignmentFlag.AlignVCenter)
        badge = QLabel(strings.get("label.experimental"))
        badge.setStyleSheet(Styles.BADGE_WARNING)
        badge.setToolTip(strings.get("tooltip.mapcache.experimental"))
        heading.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        heading.addStretch()
        layout.addLayout(heading)

        self.source = PathField(
            f"{strings.get('label.mapcache.source')} (.mdat)",
            placeholder="stalcraft/map_cache/5.0",
            caption=strings.get("dialog.mapcache.source"),
        )
        self.source.changed.connect(self._edit_source)

        self.output = PathField(
            f"{strings.get('label.mapcache.output')} (.mca)",
            placeholder=".minecraft/saves/{world}",
            caption=strings.get("dialog.mapcache.output"),
        )
        self.output.changed.connect(self._edit_output)
        self.output.reset_requested.connect(self._restore_default_output)

        if source := self._game_cache():
            self.source.value = source.as_posix()

        self.biomes = OptionWidget(
            text=strings.get("option.mapcache.biomes"),
            hint=strings.get("option.mapcache.biomes.hint"),
            checked=True,
        )
        self.backup = OptionWidget(
            text=strings.get("option.mapcache.backup"),
            hint=strings.get("option.mapcache.backup.hint"),
            checked=True,
        )

        source_card = CardWidget(strings.get("label.form.source"))
        source_card.content.addWidget(self.source)
        source_card.setMaximumWidth(MAX_FORM_WIDTH)
        layout.addWidget(source_card)

        result_card = CardWidget(strings.get("label.form.output"))
        result_card.content.addWidget(self.output)
        options = QVBoxLayout()
        options.setContentsMargins(0, 0, 0, 0)
        options.setSpacing(14)
        options.addWidget(self.biomes)
        options.addWidget(self.backup)
        result_card.content.addLayout(options)
        result_card.setMaximumWidth(MAX_FORM_WIDTH)
        layout.addWidget(result_card)
        info = self._info()
        info.setMaximumWidth(MAX_FORM_WIDTH)
        layout.addWidget(info)
        layout.addStretch()

        self.warnings = WarningsWidget()
        self.warnings.setMaximumWidth(MAX_FORM_WIDTH)
        layout.addWidget(self.warnings)

        self.submit = ProgressButton(strings.get("button.mapcache"))
        self.submit.setFixedHeight(54)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self._start_merge)
        layout.addWidget(self.submit)
        self.submit_cursor = DisabledCursor(self.submit)

    def _info(self) -> QWidget:
        info = CalloutWidget(strings.get("label.mapcache.format"))
        layout = info.content
        format_label = QLabel(strings.get("mapcache.format"))
        format_label.setStyleSheet(Styles.LABEL)
        layout.addWidget(format_label)

        limitation = QLabel(strings.get("mapcache.limitation"))
        limitation.setStyleSheet(Styles.SECONDARY)
        limitation.setWordWrap(True)
        layout.addWidget(limitation)

        credit = QLabel(strings.get("mapcache.credit"))
        credit.setStyleSheet(Styles.SECONDARY)
        layout.addWidget(credit)
        return info

    def apply_game_root(self) -> None:
        if source := self._game_cache():
            self.source.value = source.as_posix()
        self._source_changed(self.source.value)

    def apply_export_path(self, path: Path) -> None:
        self.settings.export_path = path
        if self.output not in self.touched:
            self._restore_default_output()

    def apply_path_resolution(self) -> None:
        if self.settings.resolve_paths:
            self._source_changed(self.source.value)
            self._output_changed(self.output.value)
        else:
            self._sync()

    def _game_cache(self) -> Path | None:
        game = GameRoot.find(self.settings.game_root or Path.home())
        if game and game.map_cache.is_dir():
            return game.map_cache
        return None

    def _suggested_output(self) -> Path | None:
        value = self.source.value.strip()
        if not self.settings.resolve_paths or not value:
            return None

        source = Path(value)
        if source.is_dir() and source.name:
            return self.settings.export_path / f"{source.name}_mca"
        return None

    def _restore_default_output(self) -> None:
        if output := self._suggested_output():
            self.output.value = output.as_posix()
            self.touched.discard(self.output)
            self._output_changed(self.output.value)

    def _source_changed(self, _: str) -> None:
        value = self.source.value.strip()
        if not value:
            self._refresh()
            return

        source = Path(value)

        if self.settings.resolve_paths and source.exists():
            game = GameRoot.find(source)
            resolved = game.resolve_map_cache(source) if game else source.resolve()
            if resolved != source:
                self.source.value = resolved.as_posix()
        if self.output not in self.touched:
            if output := self._suggested_output():
                self.output.value = output.as_posix()
                self.world = None
        self._refresh()

    def _edit_source(self, value: str) -> None:
        self.touched.add(self.source)
        self._source_changed(value)

    def _refresh(self) -> None:
        self.scanner.refresh(self.source.value.strip(), self.output.value.strip())

    def _output_changed(self, _: str) -> None:
        value = self.output.value.strip()
        self.world = None
        if not value:
            self._refresh()
            return

        output = Path(value)

        if self.settings.resolve_paths and output.exists():
            self.world = McWorld.find(output)
            if self.world:
                self.output.value = self.world.regions.as_posix()
        self._refresh()

    def _edit_output(self, value: str) -> None:
        self.touched.add(self.output)
        self._output_changed(value)

    def _warnings(self) -> list[str]:
        output_value = self.output.value.strip()
        if not output_value:
            return []

        output = Path(output_value)
        world = output.name
        valid = False

        if self.world:
            world = self.world.root.name
            valid = self.world.is_valid()

        overwrite = "warning.mapcache.overwrite.world" if valid else "warning.mapcache.overwrite.folder"

        return [
            message
            for condition, message in (
                (not valid, strings.get("warning.mapcache.invalid.mcworld")),
                (self.scanner.replaces, strings.get(overwrite).format(world=world)),
            )
            if condition
        ]

    def _submit_error(self) -> str | None:
        source_value = self.source.value.strip()
        output_value = self.output.value.strip()
        output = Path(output_value)
        source_error = None
        if self.scanner.error is not None:
            source_error = str(self.scanner.error)
        elif not self.scanner.busy and not self.scanner.regions:
            source_error = strings.get("tooltip.mapcache.invalid.source")

        invalid_source = not source_value or source_error is not None
        invalid_output = not output_value or output.is_file()
        self.source.set_error(source_error if source_value and invalid_source else None)
        self.output.set_error(
            strings.get("tooltip.mapcache.invalid.output") if self.output in self.touched and invalid_output else None
        )
        errors = (
            "tooltip.task.busy" if self.tasks.busy else None,
            "tooltip.mapcache.scanning" if self.scanner.busy else None,
            "tooltip.form.invalid" if invalid_source or invalid_output else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        self.output.initial_path = (self._suggested_output() or self.settings.export_path).as_posix()
        self.warnings.set_messages(self._warnings())

        if not self.submit.running:
            self.submit.setText(f"{strings.get('button.mapcache')} ({self.scanner.files:,})")

        error = self._submit_error()
        self.submit_cursor.set(self.running or error is None, strings.get(error or ""))

    def _start_merge(self) -> None:
        if self.running:
            self.tasks.cancel()
            return

        task = MapCacheTask(
            Path(self.source.value.strip()),
            Path(self.output.value.strip()),
            Options(biomes=self.biomes.checked, backup_regions=self.backup.checked),
            workers=self.settings.workers,
        )
        self.running = self.tasks.start(task)
        if self.running:
            self.submit.start()
            self.submit_cursor.set(True)
        self._sync()

    def _report(self, event: object) -> None:
        if not self.running:
            return

        match event:
            case TaskStarted():
                self.submit.start(event.total)
                self.submit_cursor.set(True)
            case TaskItem() | TaskItemFailure():
                self.submit.advance()

    def _complete(self, summary: object) -> None:
        if self.running and isinstance(summary, TaskSummary):
            self.running = False
            self.submit.finish()
            self._sync()

    def stop(self) -> None:
        self.scanner.stop()
