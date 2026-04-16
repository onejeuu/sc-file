from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Styles
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


class MapCacheTab(QWidget):
    def __init__(self):
        super().__init__()
        self.warnings = WarningsWidget()

        self._setup_warnings()
        self._setup_ui()

    def _setup_warnings(self):
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
        self.output_input.changed.connect(self._update_ui_state)

        self.main_layout.addWidget(source_label)
        self.main_layout.addWidget(self.source_input)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(output_label)
        self.main_layout.addWidget(self.output_input)

        self._build_raw_blocks()

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.warnings)

        self.merge_btn = QPushButton(Strings.get("btn_merge_regions"))
        self.merge_btn.setFixedHeight(50)
        self.merge_btn.setStyleSheet(Styles.BUTTON)
        self.merge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.merge_btn.setEnabled(False)
        self.main_layout.addWidget(self.merge_btn)

        self._update_ui_state()

    def _build_raw_blocks(self):
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Checkbox
        self.cb_raw_blocks = QCheckBox(Strings.get("cb_raw_blocks"))
        self.cb_raw_blocks.setStyleSheet(Styles.CHECKBOX)
        self.cb_raw_blocks.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_raw_blocks.setChecked(False)

        # Hint
        hint_raw_blocks = QLabel(Strings.get("hint_raw_blocks"))
        hint_raw_blocks.setStyleSheet(Styles.HINT)

        # Add to layout
        layout.addWidget(self.cb_raw_blocks)
        layout.addWidget(hint_raw_blocks)

        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(group)

    def _handle_source_change(self):
        path = Path(self.source_input.text().strip())

        if path.exists():
            resolved = resolve_mapcache_path(path)

            if resolved.as_posix() != path.as_posix():
                self.source_input.setText(resolved.as_posix())

        self._update_ui_state()

    def _update_ui_state(self):
        self.warnings.update_state()

        source = Path(self.source_input.text().strip())
        output = Path(self.output_input.text().strip())

        source_ok = is_mapcache_dir(source)
        output_ok = not output.is_file()
        is_okay = source_ok and output_ok

        checks = {
            output_ok: Strings.get("tooltip_invalid_output"),
            source_ok: Strings.get("tooltip_bad_mapcache_source"),
        }

        tooltip = checks.get(False, "")

        self.merge_btn.setEnabled(is_okay)
        self.merge_btn.setToolTip(tooltip)
        self.merge_btn.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)
