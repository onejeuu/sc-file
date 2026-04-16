from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.gui.shared.strings import Strings
from scfile.gui.shared.styles import Colors, Styles
from scfile.gui.widgets.path_input import PathInputWidget
from scfile.gui.widgets.warnings import WarningsWidget


DEFAULT_CACHE_PATH = Path.home() / "AppData/Roaming/EXBO/runtime/stalcraft/map_cache/5.0"


def is_mapcache_dir(path: Path) -> bool:
    return (
        path.exists()
        and not path.is_file()
        and path.name == "5.0"
        and path.parent.name == "map_cache"
        and any(path.rglob("*.mdat"))
    )


def resolve_mapcache_path(path: Path) -> Path:
    if is_mapcache_dir(path):
        return path

    candidates = [Path("runtime/stalcraft/map_cache/5.0"), Path("map_cache/5.0")]

    for rel in candidates:
        target = path / rel
        if is_mapcache_dir(target):
            return target

    for parent in path.parents:
        if is_mapcache_dir(parent):
            return parent

    return path


class MapCacheTab(QWidget):
    def __init__(self):
        super().__init__()
        self.warnings = WarningsWidget()

        self._setup_warnings()
        self._setup_ui()

    def _setup_warnings(self):
        def check_source():
            path = Path(self.source_input.text().strip())
            if path.as_posix() and not is_mapcache_dir(path):
                return Strings.get("warn_bad_mapcache_source")
            return None

        def check_output():
            path = Path(self.output_input.text().strip())
            if path.as_posix() and path.is_file():
                return Strings.get("warn_bad_mapcache_output")
            return None

        self.warnings.add_rule(lambda: Strings.get("warn_mdat_experimental"))
        self.warnings.add_rule(check_source)
        self.warnings.add_rule(check_output)

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
            self.source_input.setStyleSheet(f"{Styles.INPUT} QLineEdit {{ border-color: #555; }}")

        self.source_input.changed.connect(self._handle_source_change)
        self.source_input.changed.connect(self._update_ui_state)

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
        text = self.source_input.text().strip()
        if not text:
            return

        path = Path(text)
        if path.exists():
            resolved = resolve_mapcache_path(path)
            self.source_input.setText(resolved.as_posix())

            # TODO: styles classes
            is_valid = is_mapcache_dir(resolved)
            border = "#555" if is_valid else Colors.ACCENT
            self.source_input.setStyleSheet(f"{Styles.INPUT} QLineEdit {{ border-color: {border}; }}")

    def _update_ui_state(self):
        self.warnings.update_state()

        source_text = self.source_input.text().strip()
        output_text = self.output_input.text().strip()

        source_ok = is_mapcache_dir(Path(source_text))
        output_ok = bool(output_text) and not Path(output_text).is_file()
        is_okay = source_ok and output_ok

        checks = {
            output_ok: Strings.get("tooltip_bad_mapcache_output"),
            source_ok: Strings.get("tooltip_bad_mapcache_source"),
        }

        tooltip = checks.get(False, "")

        self.merge_btn.setEnabled(is_okay)
        self.merge_btn.setToolTip(tooltip)
        self.merge_btn.setCursor(Qt.CursorShape.PointingHandCursor if is_okay else Qt.CursorShape.ForbiddenCursor)
