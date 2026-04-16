from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets.option import OptionWidget
from scfile.gui.widgets.path_input import PathInputWidget
from scfile.gui.widgets.warnings import WarningsWidget


DEFAULT_CACHE_PATH = Path.home() / "AppData/Roaming/EXBO/runtime/stalcraft/map_cache/5.0"


def is_mapcache_dir(path: Path) -> bool:
    if not (path.exists() and path.is_dir()):
        return False

    if any(path.glob("*.mdat")):
        return True

    if path.name == "5.0" and path.parent.name == "map_cache":
        if any(path.glob("*/*.mdat")):
            return True

    return False


def resolve_mapcache_path(path: Path) -> Path:
    if is_mapcache_dir(path):
        return path

    for required in ["EXBO/runtime/stalcraft/map_cache/5.0", "stalcraft/map_cache/5.0"]:
        required = Path(required)

        target = path / required
        if is_mapcache_dir(target):
            return target

        candidate = required
        while candidate.parts:
            if path.match(f"*{candidate}"):
                target = path / required.relative_to(candidate)
                if is_mapcache_dir(target):
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
        self.warnings = WarningsWidget()

        self._setup_warnings()
        self._setup_ui()

    def _setup_warnings(self):
        def is_minecraft_world(path: Path) -> bool:
            return (path / "level.dat").exists()

        def check_not_world():
            if not self._is_output_set():
                return None
            out_path = Path(self.output_input.text())

            is_region = out_path.name == "region"
            has_level = is_minecraft_world(out_path.parent) if is_region else is_minecraft_world(out_path)

            if not (is_region and has_level):
                return Strings.get("warn_not_minecraft_world")
            return None

        def check_overwrite():
            if not self._is_output_set():
                return None
            out_path = Path(self.output_input.text())

            if out_path.exists() and any(out_path.glob("*.mca")):
                world_name = out_path.parent.name if out_path.name == "region" else out_path.name
                return Strings.get("warn_regions_overwrite").format(world=world_name)
            return None

        self.warnings.add_rule(check_not_world)
        self.warnings.add_rule(check_overwrite)
        self.warnings.add_rule(lambda: Strings.get("warn_mdat_experimental"))

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(5)

        source_label = QLabel(Strings.get("label_mapcache_source"))
        source_label.setStyleSheet(Styles.LABEL)

        self.source_input = PathInputWidget(
            placeholder="stalcraft/map_cache/5.0",
            caption=Strings.get("dialog_mapcache_source"),
        )

        if is_mapcache_dir(DEFAULT_CACHE_PATH):
            self.source_input.setText(DEFAULT_CACHE_PATH.as_posix())

        self.source_input.changed.connect(self._handle_source_change)

        output_label = QLabel(Strings.get("label_mapcache_output"))
        output_label.setStyleSheet(Styles.LABEL)

        self.output_input = PathInputWidget(
            placeholder=".minecraft/saves/{world}/regions",
            caption=Strings.get("dialog_mapcache_output"),
        )
        self.output_input.changed.connect(self._handle_output_change)

        self.main_layout.addWidget(source_label)
        self.main_layout.addWidget(self.source_input)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(output_label)
        self.main_layout.addWidget(self.output_input)

        self._build_options()

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.warnings)

        self.merge_btn = QPushButton(Strings.get("btn_merge_regions"))
        self.merge_btn.setFixedHeight(50)
        self.merge_btn.setStyleSheet(Styles.BUTTON)
        self.merge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.merge_btn.setEnabled(False)
        self.main_layout.addWidget(self.merge_btn)

        self._update_ui_state()

    def _build_options(self):
        self.options_group = QWidget()
        layout = QVBoxLayout(self.options_group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.cb_auto_resolve = OptionWidget(
            text=Strings.get("cb_auto_resolve"),
            hint=Strings.get("hint_auto_resolve"),
            checked=True,
        )
        self.cb_auto_resolve.changed.connect(self._handle_autoresolve)

        self.cb_raw_blocks = OptionWidget(
            text=Strings.get("cb_raw_blocks"),
            hint=Strings.get("hint_raw_blocks"),
            checked=False,
        )

        layout.addWidget(self.cb_auto_resolve)
        layout.addWidget(self.cb_raw_blocks)

        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.options_group)

    def _handle_source_change(self):
        path = Path(self.source_input.text().strip())

        if self.cb_auto_resolve.isChecked() and path.exists():
            resolved = resolve_mapcache_path(path)

            if resolved.as_posix() != path.as_posix():
                self.source_input.setText(resolved.as_posix())

        self._update_ui_state()

    def _handle_output_change(self):
        path = Path(self.output_input.text().strip())

        if self.cb_auto_resolve.isChecked() and path.exists():
            resolved = resolve_output_path(path)

            if resolved.as_posix() != path.as_posix():
                self.output_input.setText(resolved.as_posix())

        self._update_ui_state()

    def _handle_autoresolve(self):
        self._handle_source_change()
        self._handle_output_change()

    def _is_output_set(self) -> bool:
        return bool(self.output_input.text().strip())

    def _update_ui_state(self):
        self.warnings.update_state()

        source = self.source_input.text().strip()
        output = self.output_input.text().strip()

        source_ok = bool(source) and is_mapcache_dir(Path(source))
        output_ok = bool(output) and not Path(output).is_file()
        is_okay = source_ok and output_ok

        checks = {
            output_ok: Strings.get("tooltip_invalid_output"),
            source_ok: Strings.get("tooltip_bad_mapcache_source"),
        }

        tooltip = checks.get(False, "")

        self.merge_btn.setEnabled(is_okay)
        self.merge_btn.setToolTip(tooltip)
        self.merge_btn.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)
