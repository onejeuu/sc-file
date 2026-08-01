from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.app.gui import game
from scfile.app.gui.settings import Settings
from scfile.app.gui.workers import TaskManager
from scfile.app.gui.shared import strings
from scfile.app.gui.shared.styles import Styles
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathInputWidget
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.tasks import Progress
from scfile.app.tasks.mapcache import Job
from scfile.options import HandlerOptions


def is_minecraft(path: Path) -> bool:
    return (path / "level.dat").exists()


def resolve_output_path(path: Path) -> Path:
    if path.name == "region" and (path.parent / "level.dat").exists():
        return path

    if (path / "level.dat").exists():
        return path / "region"

    return path


class MapCacheTab(QWidget):
    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self._active = False

        self._setup_warnings()
        self.tasks.reported.connect(self._on_task_event)
        self.tasks.completed.connect(self._on_merge_finish)
        self.tasks.busy_changed.connect(self._sync_ui)
        self._build_ui()

    def _setup_warnings(self):
        self.warnings = WarningsWidget()
        self.warnings.add_rule(self._warn_not_minecraft_world)
        self.warnings.add_rule(self._warn_overwrite)

    def _game_map_cache(self) -> Path | None:
        installation = game.resolve(self.settings.game_root or Path.home())
        if installation and game.is_map_cache(installation.map_cache):
            return installation.map_cache
        return None

    def _warn_not_minecraft_world(self):
        if not bool(self.output.text().strip()):
            return

        output = Path(self.output.text())
        is_region = output.name == "region"
        has_level = is_minecraft(output.parent) if is_region else is_minecraft(output)

        if not (is_region and has_level):
            return strings.get("warning.mapcache.invalid_world")

    def _warn_overwrite(self):
        if not bool(self.output.text().strip()):
            return

        output = Path(self.output.text())
        is_region = output.name == "region"

        if output.exists() and any(output.glob("*.mca")):
            world_name = output.parent.name if is_region else output.name
            return strings.get("warning.mapcache.overwrite").format(world=world_name)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        source_label = QLabel(strings.get("label.mapcache.source"))
        source_label.setStyleSheet(Styles.LABEL)

        self.source = PathInputWidget(
            placeholder="stalcraft/map_cache/5.0",
            caption=strings.get("dialog.mapcache.source"),
        )

        if path := self._game_map_cache():
            self.source.setText(path.as_posix())

        self.source.changed.connect(self._on_source_changed)

        output_label = QLabel(strings.get("label.mapcache.output"))
        output_label.setStyleSheet(Styles.LABEL)

        self.output = PathInputWidget(
            placeholder=".minecraft/saves/{world}/regions",
            caption=strings.get("dialog.mapcache.output"),
        )
        self.output.changed.connect(self._on_output_changed)

        layout.addWidget(source_label)
        layout.addWidget(self.source)
        layout.addWidget(output_label)
        layout.addWidget(self.output)
        layout.addSpacing(10)
        layout.addWidget(self._build_options())
        layout.addStretch()
        layout.addWidget(self.warnings)

        self.info = QLabel(strings.get("mapcache.info"))
        self.info.setStyleSheet(Styles.MAPCACHE)
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        self.merge = QPushButton(strings.get("button.mapcache"))
        self.merge.setFixedHeight(50)
        self.merge.setStyleSheet(Styles.BUTTON_ACCENT)
        self.merge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.merge.setEnabled(False)
        self.merge.clicked.connect(self._merge)
        layout.addWidget(self.merge)

        self._sync_ui()

    def _build_options(self):
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.raw_blocks = OptionWidget(
            text=strings.get("option.mapcache.raw"),
            hint=strings.get("hint.mapcache.raw"),
            checked=False,
        )

        layout.addWidget(self.raw_blocks)

        return group

    def _merge(self):
        source = Path(self.source.text().strip())
        output = Path(self.output.text().strip())
        options = HandlerOptions(raw_blocks=self.raw_blocks.isChecked())

        self._active = True
        if not self.tasks.start(Job(source, output, options)):
            self._active = False
        self._sync_ui()

    def _on_task_event(self, event: object) -> None:
        if not self._active or not isinstance(event, Progress) or event.total is None:
            return

        label = strings.get("button.mapcache")
        self.merge.setText(f"{label} ({event.completed:,}/{event.total:,})")

    def _on_merge_finish(self, _: object) -> None:
        if not self._active:
            return

        self._active = False
        self.merge.setText(strings.get("button.mapcache"))
        self._sync_ui()

    def _on_source_changed(self):
        path = Path(self.source.text().strip())

        if self.settings.resolve_paths and path.exists():
            resolved = game.resolve_map_cache(path)

            if resolved.as_posix() != path.as_posix():
                self.source.setText(resolved.as_posix())

        self._sync_ui()

    def _on_output_changed(self):
        path = Path(self.output.text().strip())

        if self.settings.resolve_paths and path.exists():
            resolved = resolve_output_path(path)

            if resolved.as_posix() != path.as_posix():
                self.output.setText(resolved.as_posix())

        self._sync_ui()

    def apply_game_root(self) -> None:
        """Use map cache data derived from the configured game root."""

        if path := self._game_map_cache():
            self.source.setText(path.as_posix())
            self._sync_ui()

    def _sync_ui(self):
        self.warnings.update_state()

        source = self.source.text().strip()
        output = self.output.text().strip()

        source_ok = bool(source) and game.is_map_cache(Path(source))
        output_ok = bool(output) and not Path(output).is_file()
        is_okay = source_ok and output_ok and not self.tasks.busy

        if self.tasks.busy:
            tooltip = "tooltip.task.busy"
        else:
            tooltip = {
                output_ok: "tooltip.mapcache.invalid.output",
                source_ok: "tooltip.mapcache.invalid.source",
            }.get(False, "")

        self.merge.setEnabled(is_okay)
        self.merge.setToolTip(strings.get(tooltip))
        self.merge.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)
