from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.core import Options
from scfile.gui import workers
from scfile.gui.shared import strings
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets import OptionWidget, PathInputWidget, WarningsWidget
from scfile.gui.workers.mapcache import MapCacheWorker


DEFAULT_CACHE_PATH = Path.home() / "AppData/Roaming/EXBO/runtime/stalcraft/map_cache/5.0"


def is_mapcache(path: Path) -> bool:
    if not (path.exists() and path.is_dir()):
        return False

    if any(path.glob("*/*.mdat")):
        return True

    return False


def is_minecraft(path: Path) -> bool:
    return (path / "level.dat").exists()


def resolve_mapcache_path(path: Path) -> Path:
    if is_mapcache(path):
        return path

    for root in ["EXBO/runtime/stalcraft/map_cache/5.0", "stalcraft/map_cache/5.0"]:
        required = Path(root)

        target = path / required
        if is_mapcache(target):
            return target

        candidate = required
        while candidate.parts:
            if path.match(f"*{candidate}"):
                target = path / required.relative_to(candidate)
                if is_mapcache(target):
                    return target
                break
            candidate = candidate.parent

    return path


def resolve_output_path(path: Path) -> Path:
    if path.name == "region" and (path.parent / "level.dat").exists():
        return path

    if (path / "level.dat").exists():
        return path / "region"

    return path


class MapCacheTab(QWidget):
    def __init__(self):
        super().__init__()

        self._setup_warnings()
        self._setup_merger()
        self._build_ui()

    def _setup_warnings(self):
        self.warnings = WarningsWidget()
        self.warnings.add_rule(self._warn_not_minecraft_world)
        self.warnings.add_rule(self._warn_overwrite)

    def _setup_merger(self):
        self._merger: MapCacheWorker | None = None
        self._merger_thread: QThread | None = None

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

        if is_mapcache(DEFAULT_CACHE_PATH):
            self.source.setText(DEFAULT_CACHE_PATH.as_posix())

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

        self.merge = QPushButton(strings.get("button.mapcache.merge"))
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

        self.auto_resolve = OptionWidget(
            text=strings.get("option.mapcache.resolve"),
            hint=strings.get("hint.mapcache.resolve"),
            checked=True,
        )
        self.auto_resolve.changed.connect(self._on_autoresolve_changed)

        self.raw_blocks = OptionWidget(
            text=strings.get("option.mapcache.raw"),
            hint=strings.get("hint.mapcache.raw"),
            checked=False,
        )

        layout.addWidget(self.auto_resolve)
        layout.addWidget(self.raw_blocks)

        return group

    def _merge(self):
        source = Path(self.source.text().strip())
        output = Path(self.output.text().strip())
        options = Options(raw_blocks=self.raw_blocks.isChecked())

        self.merge.setEnabled(False)

        self._merger = MapCacheWorker(source, output, options)
        self._merger_thread = workers.execute(self._merger, on_done=self._on_merge_finish)

    def _on_merge_finish(self):
        self._merger = None
        self._merger_thread = None
        self.merge.setEnabled(True)

    def _on_source_changed(self):
        path = Path(self.source.text().strip())

        if self.auto_resolve.isChecked() and path.exists():
            resolved = resolve_mapcache_path(path)

            if resolved.as_posix() != path.as_posix():
                self.source.setText(resolved.as_posix())

        self._sync_ui()

    def _on_output_changed(self):
        path = Path(self.output.text().strip())

        if self.auto_resolve.isChecked() and path.exists():
            resolved = resolve_output_path(path)

            if resolved.as_posix() != path.as_posix():
                self.output.setText(resolved.as_posix())

        self._sync_ui()

    def _on_autoresolve_changed(self):
        self._on_source_changed()
        self._on_output_changed()

    def _sync_ui(self):
        self.warnings.update_state()

        source = self.source.text().strip()
        output = self.output.text().strip()

        source_ok = bool(source) and is_mapcache(Path(source))
        output_ok = bool(output) and not Path(output).is_file()
        is_okay = source_ok and output_ok

        tooltip = {
            output_ok: "tooltip.mapcache.invalid.output",
            source_ok: "tooltip.mapcache.invalid.source",
        }.get(False, "")

        self.merge.setEnabled(is_okay)
        self.merge.setToolTip(strings.get(tooltip))
        self.merge.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)

    def closeEvent(self, event: QCloseEvent):
        if self._merger:
            self._merger.stop()

        super().closeEvent(event)
