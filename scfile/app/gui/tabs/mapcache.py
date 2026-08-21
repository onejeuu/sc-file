from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app import game
from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.game import MinecraftWorld
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.link import LinkWidget
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
        self.world: MinecraftWorld | None = None
        self.running = False
        self._build_ui()

        self.tasks.busy_changed.connect(self._sync)
        self.tasks.reported.connect(self._report)
        self.tasks.completed.connect(self._complete)
        self.scanner.changed.connect(self._sync)
        self._refresh()
        self._sync()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.source = PathField(
            strings.get("label.mapcache.source"),
            placeholder="stalcraft/map_cache/5.0",
            caption=strings.get("dialog.mapcache.source"),
        )
        self.source.changed.connect(self._edit_source)

        if source := self._game_cache():
            self.source.value = source.as_posix()

        self.output = PathField(
            strings.get("label.mapcache.output"),
            placeholder=".minecraft/saves/{world}",
            caption=strings.get("dialog.mapcache.output"),
        )
        self.output.changed.connect(self._edit_output)

        self.raw_blocks = OptionWidget(
            text=strings.get("option.mapcache.raw"),
            hint=strings.get("hint.mapcache.raw"),
        )

        layout.addWidget(self.source)
        layout.addWidget(self.output)
        layout.addSpacing(10)
        layout.addWidget(self.raw_blocks)
        layout.addStretch()

        self.warnings = WarningsWidget()
        layout.addWidget(self.warnings)

        layout.addWidget(self._info())

        self.submit = ProgressButton(strings.get("button.mapcache"))
        self.submit.setFixedHeight(50)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self._start_merge)
        layout.addWidget(self.submit)
        self.submit_cursor = DisabledCursor(self.submit)

    def _info(self) -> QWidget:
        info = QWidget()
        layout = QVBoxLayout(info)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel(strings.get("mapcache.preview"))
        title.setStyleSheet(Styles.LABEL)
        layout.addWidget(title)

        version = QLabel(strings.get("mapcache.version"))
        version.setStyleSheet(Styles.MAPCACHE)
        layout.addWidget(version)

        limitation = QLabel(strings.get("mapcache.limitation"))
        limitation.setStyleSheet(Styles.MAPCACHE)
        limitation.setWordWrap(True)
        layout.addWidget(limitation)

        footer = QHBoxLayout()
        credit = QLabel(strings.get("mapcache.credit"))
        credit.setStyleSheet(Styles.MAPCACHE)
        footer.addWidget(credit)
        footer.addStretch()

        language = strings.LANG.lower()
        url = f"https://sc-file.readthedocs.io/{language}/latest/usage/mapcache.html"
        footer.addWidget(LinkWidget(strings.get("mapcache.guide"), url))
        layout.addLayout(footer)
        return info

    def apply_game_root(self) -> None:
        if source := self._game_cache():
            self.source.value = source.as_posix()
        self._sync()

    def apply_path_resolution(self) -> None:
        if self.settings.resolve_paths:
            self._source_changed(self.source.value)
            self._output_changed(self.output.value)
        else:
            self._sync()

    def _game_cache(self) -> Path | None:
        installation = game.resolve(self.settings.game_root or Path.home())
        if installation and installation.map_cache.is_dir():
            return installation.map_cache
        return None

    def _source_changed(self, _: str) -> None:
        value = self.source.value.strip()
        if not value:
            self._refresh()
            return

        source = Path(value)

        if self.settings.resolve_paths and source.exists():
            resolved = game.resolve_map_cache(source)
            if resolved != source:
                self.source.value = resolved.as_posix()
        self._refresh()

    def _edit_source(self, value: str) -> None:
        self.touched.add(self.source)
        self._source_changed(value)

    def _refresh(self) -> None:
        self.scanner.refresh(self.source.value.strip())

    def _output_changed(self, _: str) -> None:
        value = self.output.value.strip()
        if not value:
            self.world = None
            self._sync()
            return

        output = Path(value)

        if self.settings.resolve_paths and output.exists():
            self.world = game.resolve_minecraft_world(output)
            if self.world:
                self.output.value = self.world.regions.as_posix()
        self._sync()

    def _edit_output(self, value: str) -> None:
        self.touched.add(self.output)
        self._output_changed(value)

    def _warnings(self) -> list[str]:
        output_value = self.output.value.strip()
        if not output_value:
            return []

        output = Path(output_value)
        regions = any(output.glob("*.mca"))
        world = output.name
        valid = False

        if self.world:
            world = self.world.root.name
            valid = self.world.is_valid()

        overwrite = "warning.mapcache.overwrite.world" if valid else "warning.mapcache.overwrite.folder"

        return [
            message
            for condition, message in (
                (not valid, strings.get("warning.mapcache.invalid_world")),
                (regions, strings.get(overwrite).format(world=world)),
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
            "tooltip.invalid.form" if invalid_source or invalid_output else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        self.warnings.set_messages(self._warnings())

        error = self._submit_error()
        self.submit_cursor.set(self.running or error is None, strings.get(error or ""))

    def _start_merge(self) -> None:
        if self.running:
            self.tasks.cancel()
            return

        task = MapCacheTask(
            Path(self.source.value.strip()),
            Path(self.output.value.strip()),
            Options(raw_blocks=self.raw_blocks.checked),
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
