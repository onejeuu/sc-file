from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget

from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.game import GameRoot
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.path import PathField
from scfile.app.gui.widgets.progress import ProgressButton
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.tasks.mapmerge import MapMergeTask
from scfile.convert import mapmerge
from scfile.options import Options


IGNORED_MAP_FOLDERS = frozenset(("sound", "textures"))


class MapMergeTab(QWidget):
    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self.source_touched = False
        self.output_touched = False
        self.running = False
        self.game: GameRoot | None = None
        self._build_ui()

        self.tasks.busy_changed.connect(self._sync)
        self.tasks.reported.connect(self._report)
        self.tasks.completed.connect(self._complete)
        self.apply_game_root()
        self._sync()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.source = PathField(
            f"{strings.get('label.mapmerge.source')} (.ol)",
            placeholder="pda/map",
            caption=strings.get("dialog.mapmerge.source"),
        )
        self.source.changed.connect(self._edit_source)
        self.source.text_changed.connect(self._source_changed)

        self.map_label = QLabel(strings.get("label.mapmerge.map"))
        self.map_label.setStyleSheet(Styles.LABEL)
        self.map = QComboBox()
        self.map.setStyleSheet(Styles.COMBO)
        self.map.setCursor(Qt.CursorShape.PointingHandCursor)
        self.map.setPlaceholderText(strings.get("placeholder.mapmerge.map"))
        self.map.currentIndexChanged.connect(self._map_changed)

        self.output = PathField(
            f"{strings.get('label.mapmerge.output')} (.jpg)",
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.mapmerge.output"),
            mode="save",
            file_filter="JPEG (*.jpg)",
            default_suffix=".jpg",
        )
        self.output.changed.connect(self._edit_output)

        layout.addWidget(self.source)
        layout.addWidget(self.map_label)
        layout.addWidget(self.map)
        layout.addWidget(self.output)
        self.map_cursor = DisabledCursor(self.map)
        self.map_cursor.set(False, strings.get("tooltip.mapmerge.map"))

        layout.addStretch()

        self.warnings = WarningsWidget()
        layout.addWidget(self.warnings)

        self.submit = ProgressButton(strings.get("button.mapmerge"))
        self.submit.setFixedHeight(50)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self._start_merge)
        layout.addWidget(self.submit)
        self.submit_cursor = DisabledCursor(self.submit)

    def apply_export_path(self, path: Path) -> None:
        self.settings.export_path = path
        self._source_changed(self.source.value)

    def apply_game_root(self) -> None:
        if self.settings.resolve_paths and self.settings.game_root is not None:
            self.source.value = self.settings.game_root.as_posix()
        else:
            self._source_changed(self.source.value)

    def apply_path_resolution(self) -> None:
        self._source_changed(self.source.value)

    def _suggested_output(self) -> Path | None:
        source = self._source_path()
        if not self.settings.resolve_paths or source is None:
            return None
        return self.settings.export_path / f"{source.name}.jpg"

    def _source_changed(self, _: str) -> None:
        value = self.source.value.strip()
        source = Path(value) if value else None

        if source is not None:
            resolved = self._resolve_source(source)
            if resolved != source:
                self.source.value = resolved.as_posix()
                return

        self._update_maps(source)
        self._update_output()
        self._sync()

    def _map_changed(self, _: int) -> None:
        self._update_output()
        self._sync()

    def _resolve_source(self, source: Path) -> Path:
        if not self.settings.resolve_paths or not source.is_dir():
            return source

        source = source.resolve()
        game = GameRoot.find(source)
        if game is None:
            return source

        pda = (game.assets / "pda").resolve()
        return source if source.is_relative_to(pda) else pda

    def _update_maps(self, source: Path | None) -> None:
        if source is None:
            self._clear_maps()
            return

        source = source.resolve()
        game = GameRoot.find(source)
        if game is None:
            self._clear_maps()
            return

        pda = (game.assets / "pda").resolve()
        if source == pda:
            self._load_maps(game)
            return

        if source.parent == pda:
            self._load_maps(game, source)
            return

        self._clear_maps()

    def _update_output(self) -> None:
        if self.settings.resolve_paths:
            suggested = self._suggested_output()
            self.output.value = suggested.as_posix() if suggested else ""

    def _load_maps(self, game: GameRoot, selected: Path | None = None) -> None:
        folders = self._map_folders(game)
        if selected is not None and selected not in folders:
            self._clear_maps("tooltip.mapmerge.empty.map")
            return

        current = selected or self.map.currentData()
        self.game = game

        with QSignalBlocker(self.map):
            self.map.clear()

            for folder in folders:
                title = strings.mapmerge_map(folder.name)
                label = folder.name if title == folder.name else f"{title} ({folder.name})"
                self.map.addItem(label, folder)

            if not folders:
                self._disable_maps("tooltip.mapmerge.empty.map")
                return

            enabled = selected is None
            self.map_label.setEnabled(enabled)
            tooltip = "tooltip.mapmerge.map" if enabled else "tooltip.mapmerge.fixed.map"
            self.map_cursor.set(enabled, strings.get(tooltip))
            self.map.setCurrentIndex(folders.index(current) if current in folders else 0)

    def _clear_maps(self, tooltip: str = "tooltip.mapmerge.map") -> None:
        self.game = None
        with QSignalBlocker(self.map):
            self.map.clear()
        self._disable_maps(tooltip)

    def _disable_maps(self, tooltip: str) -> None:
        self.map_label.setEnabled(False)
        self.map_cursor.set(False, strings.get(tooltip))

    @staticmethod
    def _map_folders(game: GameRoot) -> tuple[Path, ...]:
        folder = game.assets / "pda"

        try:
            paths = tuple(sorted(path for path in folder.iterdir() if path.is_dir()))

        except OSError:
            return ()

        maps: list[Path] = []
        for path in paths:
            if path.name in IGNORED_MAP_FOLDERS:
                continue

            try:
                if mapmerge.scan(path):
                    maps.append(path)

            except OSError:
                continue

        return tuple(maps)

    def _edit_source(self, value: str) -> None:
        self.source_touched = True
        self._source_changed(value)

    def _edit_output(self, _: str) -> None:
        self.output_touched = True
        self._sync()

    def _source_path(self) -> Path | None:
        if self.game is not None:
            path = self.map.currentData()
            if isinstance(path, Path):
                return path

        value = self.source.value.strip()
        return Path(value) if value else None

    def _source_invalid(self) -> bool:
        source = self._source_path()
        if source is None:
            return True

        if not source.is_dir():
            return True

        try:
            return not mapmerge.scan(source)

        except OSError:
            return True

    def _output_invalid(self) -> bool:
        value = self.output.value.strip()
        output = Path(value)
        return not value or output.is_dir() or output.suffix.lower() != ".jpg"

    def _submit_error(self) -> str | None:
        errors = (
            "tooltip.task.busy" if self.tasks.busy and not self.running else None,
            "tooltip.form.invalid" if self._source_invalid() or self._output_invalid() else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        suggested = self._suggested_output()
        self.output.initial_path = (suggested or self.settings.export_path).as_posix()

        source_invalid = self.source_touched and self._source_invalid()
        source_error = strings.get("tooltip.mapmerge.invalid.source") if source_invalid else None
        self.source.set_error(source_error)

        output_invalid = self.output_touched and self._output_invalid()
        output_error = strings.get("tooltip.mapmerge.invalid.output") if output_invalid else None
        self.output.set_error(output_error)

        output = Path(self.output.value.strip())
        warnings = (strings.get("warning.mapmerge.overwrite"),) if output.is_file() else ()
        self.warnings.set_messages(warnings)

        error = self._submit_error()
        self.submit_cursor.set(self.running or error is None, strings.get(error or ""))

    def _start_merge(self) -> None:
        if self.running:
            self.tasks.cancel()
            return

        source = self._source_path()
        if source is None:
            return

        task = MapMergeTask(
            source,
            Path(self.output.value.strip()),
            Options(),
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
