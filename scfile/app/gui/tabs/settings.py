from pathlib import Path

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app import files
from scfile.app.consts import DEFAULT_OUTPUT
from scfile.app.game import GameRoot
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathInputWidget


ICON_SIZE = QSize(16, 16)


def _icon(name: str) -> QIcon:
    return QIcon(str(files.resource(f"assets/settings.{name}.png")))


class SettingsTab(QWidget):
    changed = Signal()
    game_root_changed = Signal()
    path_resolution_changed = Signal()
    verbose_changed = Signal(bool)
    export_path_changed = Signal(object)

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)

        general = QLabel(strings.get("label.settings.general"))
        general.setStyleSheet(Styles.SECTION)
        layout.addWidget(general)
        layout.addSpacing(8)

        self.resolve_paths = OptionWidget(
            text=strings.get("option.settings.resolve"),
            hint=strings.get("option.settings.resolve.hint"),
            checked=self.settings.resolve_paths,
            icon=_icon("resolve_paths"),
        )
        self.resolve_paths.changed.connect(self._set_path_resolution)
        layout.addWidget(self.resolve_paths)
        layout.addSpacing(12)

        self.verbose = OptionWidget(
            text=strings.get("option.settings.verbose"),
            hint=strings.get("option.settings.verbose.hint"),
            checked=self.settings.verbose,
            icon=_icon("verbose"),
        )
        self.verbose.changed.connect(self._set_verbose)
        layout.addWidget(self.verbose)
        layout.addSpacing(20)

        paths = QLabel(strings.get("label.settings.paths"))
        paths.setStyleSheet(Styles.SECTION)
        layout.addWidget(paths)
        layout.addSpacing(8)

        root_header = QWidget()
        root_layout = QHBoxLayout(root_header)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(5)

        root_icon = QLabel()
        root_icon.setPixmap(_icon("gameroot").pixmap(ICON_SIZE))
        root_layout.addWidget(root_icon)

        root_label = QLabel(strings.get("label.settings.game"))
        root_label.setStyleSheet(Styles.LABEL)
        root_layout.addWidget(root_label)
        root_layout.addStretch()
        self.root = PathInputWidget(
            placeholder="C:/EXBO/runtime/stalcraft",
            caption=strings.get("dialog.settings.game"),
        )
        if self.settings.game_root is not None:
            self.root.value = self.settings.game_root.as_posix()
        self.root.changed.connect(self._set_game_root)

        hint = QLabel(strings.get("label.settings.game.hint"))
        hint.setStyleSheet(Styles.HINT)
        hint.setWordWrap(True)

        layout.addWidget(root_header)
        layout.addWidget(self.root)
        layout.addWidget(hint)
        layout.addSpacing(12)

        export_header = QWidget()
        export_layout = QHBoxLayout(export_header)
        export_layout.setContentsMargins(0, 0, 0, 0)
        export_layout.setSpacing(5)

        export_icon = QLabel()
        export_icon.setPixmap(_icon("export_path").pixmap(ICON_SIZE))
        export_layout.addWidget(export_icon)

        export_label = QLabel(strings.get("label.settings.export"))
        export_label.setStyleSheet(Styles.LABEL)
        export_layout.addWidget(export_label)
        export_layout.addStretch()

        self.export = PathInputWidget(
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.settings.export"),
        )
        self.export.value = self.settings.export_path.as_posix()
        self.export.changed.connect(self._set_export_path)
        export_hint = QLabel(strings.get("label.settings.export.hint"))
        export_hint.setStyleSheet(Styles.HINT)

        layout.addWidget(export_header)
        layout.addWidget(self.export)
        layout.addWidget(export_hint)
        layout.addSpacing(12)

        layout.addStretch()

    def _set_game_root(self, value: str) -> None:
        value = value.strip()
        if not value:
            self.root.invalid = False
            self.settings.game_root = None
            self.changed.emit()
            self.game_root_changed.emit()
            return

        source = Path(value)
        resolver = GameRoot.find if self.settings.resolve_paths else GameRoot.from_path
        game = resolver(source)

        if game is None:
            self.root.invalid = True
            return

        self.root.invalid = False
        self.settings.game_root = game.root
        if self.settings.resolve_paths:
            self.root.value = game.root.as_posix()
        self.changed.emit()
        self.game_root_changed.emit()

    def _set_path_resolution(self, enabled: bool) -> None:
        self.settings.resolve_paths = enabled
        value = self.root.value.strip()
        root_changed = False

        if enabled and value:
            game = GameRoot.find(Path(value))
            if game is not None:
                self.root.invalid = False
                self.settings.game_root = game.root
                self.root.value = game.root.as_posix()
                root_changed = True

        self.changed.emit()
        if root_changed:
            self.game_root_changed.emit()
        self.path_resolution_changed.emit()

    def _set_verbose(self, enabled: bool) -> None:
        self.settings.verbose = enabled
        self.changed.emit()
        self.verbose_changed.emit(enabled)

    def _set_export_path(self, value: str) -> None:
        path = Path(value.strip()) if value.strip() else DEFAULT_OUTPUT
        if path.is_file():
            self.export.invalid = True
            return

        self.export.invalid = False
        self.settings.export_path = path
        self.export.value = path.as_posix()
        self.changed.emit()
        self.export_path_changed.emit(path)

    def apply_export_path(self, path: Path) -> None:
        self.export.invalid = False
        self.export.value = path.as_posix()
