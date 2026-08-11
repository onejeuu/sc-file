from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.app import game
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathInputWidget
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.options import Options


class MapCacheTab(QWidget):
    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self._build_ui()

        self.tasks.busy_changed.connect(self._sync)
        self._sync()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        source_label = QLabel(strings.get("label.mapcache.source"))
        source_label.setStyleSheet(Styles.LABEL)
        self.source = PathInputWidget(
            placeholder="stalcraft/map_cache/5.0",
            caption=strings.get("dialog.mapcache.source"),
        )
        self.source.changed.connect(self._source_changed)

        if source := self._game_cache():
            self.source.value = source.as_posix()

        output_label = QLabel(strings.get("label.mapcache.output"))
        output_label.setStyleSheet(Styles.LABEL)
        self.output = PathInputWidget(
            placeholder=".minecraft/saves/{world}/regions",
            caption=strings.get("dialog.mapcache.output"),
        )
        self.output.changed.connect(self._output_changed)

        self.raw_blocks = OptionWidget(
            text=strings.get("option.mapcache.raw"),
            hint=strings.get("hint.mapcache.raw"),
        )

        layout.addWidget(source_label)
        layout.addWidget(self.source)
        layout.addWidget(output_label)
        layout.addWidget(self.output)
        layout.addSpacing(10)
        layout.addWidget(self.raw_blocks)
        layout.addStretch()

        self.warnings = WarningsWidget()
        layout.addWidget(self.warnings)

        info = QLabel(strings.get("mapcache.info"))
        info.setStyleSheet(Styles.MAPCACHE)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.submit = QPushButton(strings.get("button.mapcache"))
        self.submit.setFixedHeight(50)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self._start_merge)
        layout.addWidget(self.submit)

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
        if installation and game.is_map_cache(installation.map_cache):
            return installation.map_cache
        return None

    def _source_changed(self, _: str) -> None:
        source = Path(self.source.value.strip())
        if self.settings.resolve_paths and source.exists():
            resolved = game.resolve_map_cache(source)
            if resolved != source:
                self.source.value = resolved.as_posix()
        self._sync()

    def _output_changed(self, _: str) -> None:
        output = Path(self.output.value.strip())
        if self.settings.resolve_paths and output.exists():
            resolved = game.resolve_minecraft_regions(output)
            if resolved != output:
                self.output.value = resolved.as_posix()
        self._sync()

    def _warnings(self) -> list[str]:
        output_value = self.output.value.strip()
        if not output_value:
            return []

        output = Path(output_value)
        is_regions = output.name == "region"
        valid_world = is_regions and game.is_minecraft_world(output.parent)
        has_regions = output.exists() and any(output.glob("*.mca"))
        world = output.parent.name if is_regions else output.name

        return [
            message
            for condition, message in (
                (not valid_world, strings.get("warning.mapcache.invalid_world")),
                (has_regions, strings.get("warning.mapcache.overwrite").format(world=world)),
            )
            if condition
        ]

    def _submit_error(self) -> str | None:
        source_value = self.source.value.strip()
        output_value = self.output.value.strip()
        source = Path(source_value)
        output = Path(output_value)
        errors = (
            "tooltip.task.busy" if self.tasks.busy else None,
            "tooltip.mapcache.invalid.source" if not source_value or not game.is_map_cache(source) else None,
            "tooltip.mapcache.invalid.output" if not output_value or output.is_file() else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        self.warnings.set_messages(self._warnings())

        error = self._submit_error()
        self.submit.setEnabled(error is None)
        self.submit.setToolTip(strings.get(error or ""))
        cursor = Qt.CursorShape.PointingHandCursor if error is None else Qt.CursorShape.ForbiddenCursor
        self.submit.setCursor(cursor)

    def _start_merge(self) -> None:
        task = MapCacheTask(
            Path(self.source.value.strip()),
            Path(self.output.value.strip()),
            Options(region={"raw_blocks": self.raw_blocks.checked}),
        )
        self.tasks.start(task)
        self._sync()
