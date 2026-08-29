from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QStyledItemDelegate, QVBoxLayout, QWidget

from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.game import GameRegion, GameRoot
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.encoding import ImageEncodingWidget
from scfile.app.gui.widgets.path import PathField
from scfile.app.gui.widgets.progress import ProgressButton
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.localization import system_language
from scfile.app.tasks.mapmerge import MapImageFormat, MapMergeTask
from scfile.convert import mapmerge
from scfile.options import Options


IGNORED_MAP_SUFFIXES = ("textures", "sound", "overlay")


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

        self.region_label = QLabel(strings.get("label.mapmerge.region"))
        self.region_label.setStyleSheet(Styles.LABEL)
        self.region = QComboBox()
        self.region.setStyleSheet(Styles.COMBO)
        self.region.setCursor(Qt.CursorShape.PointingHandCursor)
        self.region.setItemDelegate(QStyledItemDelegate())
        self.region.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.region.setPlaceholderText(strings.get("placeholder.mapmerge.region"))
        self.region.activated.connect(self._region_changed)

        self.map_label = QLabel(strings.get("label.mapmerge.map"))
        self.map_label.setStyleSheet(Styles.LABEL)
        self.map = QComboBox()
        self.map.setStyleSheet(Styles.COMBO)
        self.map.setCursor(Qt.CursorShape.PointingHandCursor)
        self.map.setItemDelegate(QStyledItemDelegate())
        self.map.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.map.setPlaceholderText(strings.get("placeholder.mapmerge.map"))
        self.map.activated.connect(self._map_changed)

        self.encoding = ImageEncodingWidget()
        self.encoding.changed.connect(self._format_changed)
        self.output = PathField(
            strings.get("label.mapmerge.output"),
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.mapmerge.output"),
            mode="save",
            file_filter="Images (*.jpg *.jpeg *.png)",
            default_suffix=self.encoding.format.suffix,
        )
        self.output.changed.connect(self._edit_output)

        layout.addWidget(self.source)
        layout.addWidget(self.region_label)
        layout.addWidget(self.region)
        layout.addWidget(self.map_label)
        layout.addWidget(self.map)
        layout.addWidget(self.output)
        layout.addWidget(self.encoding)
        self.region_cursor = DisabledCursor(self.region)
        self.region_cursor.set(False, strings.get("tooltip.mapmerge.region"))
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
        if not self.settings.resolve_paths or self._source_invalid():
            return None

        name = self._source_name()
        return self.settings.export_path / f"{name}{self.encoding.format.suffix}" if name else None

    def _source_changed(self, _: str) -> None:
        value = self.source.value.strip()
        source = Path(value) if value else None

        if source is not None:
            resolved = self._resolve_source(source)
            if resolved != source:
                self.source.value = resolved.as_posix()
                return

        self._update_game(source)
        self._update_output()
        self._sync()

    def _region_changed(self, _: int) -> None:
        if self.game is not None:
            self._load_maps()
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

    def _update_game(self, source: Path | None) -> None:
        if source is None:
            self._clear_game()
            return

        source = source.resolve()
        game = GameRoot.find(source)
        if game is None:
            self._clear_game()
            return

        pda = (game.assets / "pda").resolve()
        if source == pda:
            self._load_game(game)
            return

        if source.parent == pda:
            self._load_game(game)
            return

        self._clear_game()

    def _update_output(self) -> None:
        if self.settings.resolve_paths:
            suggested = self._suggested_output()
            self.output.value = suggested.as_posix() if suggested else ""

    def _load_game(self, game: GameRoot) -> None:
        self.game = game
        self._load_regions()
        self._load_maps()

    def _load_regions(self) -> None:
        if self.game is None:
            return

        regions = self.game.regions
        current = self.region.currentData()
        preferred = GameRegion(system_language().lower())
        selected = current if current in regions else preferred
        if selected not in regions:
            selected = regions[0] if regions else None

        self.region.clear()
        for region in regions:
            self.region.addItem(region.upper(), region)
        self.region.setCurrentIndex(regions.index(selected) if selected else -1)

        enabled = bool(regions)
        self.region_label.setEnabled(enabled)
        self.region_cursor.set(enabled, strings.get("tooltip.mapmerge.region"))

    def _load_maps(self) -> None:
        if self.game is None:
            return

        names = self._map_names(self.game, self._region())
        fixed = self._fixed_map()
        if fixed is not None and fixed not in names:
            self._clear_maps("tooltip.mapmerge.empty.map")
            return

        current = fixed or self.map.currentData()
        self.map.clear()
        for name in names:
            title = strings.get(f"mapmerge.map.{name}", name)
            label = name if title == name else f"{title} ({name})"
            self.map.addItem(label, name)

        if not names:
            self._disable_maps("tooltip.mapmerge.empty.map")
            return

        enabled = fixed is None
        self.map_label.setEnabled(enabled)
        tooltip = "tooltip.mapmerge.map" if enabled else "tooltip.mapmerge.fixed.map"
        self.map_cursor.set(enabled, strings.get(tooltip))
        self.map.setCurrentIndex(names.index(current) if current in names else 0)

    def _clear_game(self) -> None:
        self.game = None
        self.region.clear()
        self.region_label.setEnabled(False)
        self.region_cursor.set(False, strings.get("tooltip.mapmerge.region"))
        self._clear_maps()

    def _clear_maps(self, tooltip: str = "tooltip.mapmerge.map") -> None:
        self.map.clear()
        self._disable_maps(tooltip)

    def _disable_maps(self, tooltip: str) -> None:
        self.map_label.setEnabled(False)
        self.map_cursor.set(False, strings.get(tooltip))

    def _region(self) -> GameRegion:
        value = self.region.currentData()
        return GameRegion(value) if isinstance(value, str) else GameRegion(system_language().lower())

    def _fixed_map(self) -> str | None:
        value = self.source.value.strip()
        if not value or self.game is None:
            return None

        source = Path(value).resolve()
        pda = (self.game.assets / "pda").resolve()
        return source.name if source.parent == pda else None

    @staticmethod
    def _map_names(game: GameRoot, region: GameRegion) -> tuple[str, ...]:
        names: set[str] = set()

        for layer in game.asset_layers(region):
            folder = layer / "pda"
            try:
                names.update(
                    path.name
                    for path in folder.iterdir()
                    if path.is_dir() and not path.name.lower().endswith(IGNORED_MAP_SUFFIXES)
                )

            except OSError:
                continue

        maps: list[str] = []
        for name in sorted(names):
            try:
                if mapmerge.collect(game.asset_paths(Path("pda") / name, region)):
                    maps.append(name)

            except OSError:
                continue

        return tuple(maps)

    def _edit_source(self, value: str) -> None:
        self.source_touched = True
        self._source_changed(value)

    def _edit_output(self, _: str) -> None:
        self.output_touched = True
        if image_format := MapImageFormat.parse(Path(self.output.value.strip())):
            self._set_format(image_format)
        self._sync()

    def _format_changed(self, image_format: MapImageFormat) -> None:
        self.output.default_suffix = image_format.suffix
        if value := self.output.value.strip():
            self.output.value = Path(value).with_suffix(image_format.suffix).as_posix()
            self.output_touched = True
        self._sync()

    def _set_format(self, image_format: MapImageFormat) -> None:
        self.encoding.format = image_format
        self.output.default_suffix = image_format.suffix

    def _sources(self) -> tuple[Path, ...]:
        if self.game is not None:
            name = self._map_name()
            return self.game.asset_paths(Path("pda") / name, self._region()) if name else ()

        value = self.source.value.strip()
        return (Path(value),) if value else ()

    def _source_name(self) -> str | None:
        if self.game is not None:
            return self._map_name()

        value = self.source.value.strip()
        return Path(value).name if value else None

    def _map_name(self) -> str | None:
        value = self.map.currentData()
        return value if isinstance(value, str) else None

    def _source_invalid(self) -> bool:
        sources = self._sources()
        if not sources:
            return True

        try:
            return not mapmerge.collect(sources)

        except OSError:
            return True

    def _output_invalid(self) -> bool:
        value = self.output.value.strip()
        output = Path(value)
        return not value or output.is_dir() or MapImageFormat.parse(output) is None

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

        sources = self._sources()
        if not sources:
            return

        tiles = mapmerge.collect(sources)
        if not tiles:
            return

        task = MapMergeTask(
            tiles,
            Path(self.output.value.strip()),
            Options(),
            self.encoding.save,
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
