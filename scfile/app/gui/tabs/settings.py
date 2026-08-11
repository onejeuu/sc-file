from pathlib import Path

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app import files, game
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathInputWidget


ICON_SIZE = QSize(20, 20)


def _icon(name: str) -> QIcon:
    return QIcon(str(files.resource(f"assets/settings.{name}.png")))


class SettingsTab(QWidget):
    changed = Signal()
    game_root_changed = Signal()
    path_resolution_changed = Signal()
    verbose_changed = Signal(bool)
    output_memory_changed = Signal(bool)

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)

        root_header = QWidget()
        root_layout = QHBoxLayout(root_header)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(5)

        root_icon = QLabel()
        root_icon.setPixmap(_icon("gameroot").pixmap(ICON_SIZE))
        root_layout.addWidget(root_icon)

        root_label = QLabel(strings.get("label.settings.game_root"))
        root_label.setStyleSheet(Styles.LABEL)
        root_layout.addWidget(root_label)
        root_layout.addStretch()
        self.root = PathInputWidget(
            placeholder="C:/EXBO/runtime/stalcraft",
            caption=strings.get("dialog.settings.game_root"),
        )
        if self.settings.game_root is not None:
            self.root.value = self.settings.game_root.as_posix()
        self.root.changed.connect(self._set_game_root)

        hint = QLabel(strings.get("hint.settings.game_root"))
        hint.setStyleSheet(Styles.HINT)
        hint.setWordWrap(True)

        layout.addWidget(root_header)
        layout.addWidget(self.root)
        layout.addWidget(hint)
        layout.addSpacing(12)

        self.resolve_paths = OptionWidget(
            text=strings.get("option.settings.resolve_paths"),
            hint=strings.get("hint.settings.resolve_paths"),
            checked=self.settings.resolve_paths,
            icon=_icon("resolve_paths"),
        )
        self.resolve_paths.changed.connect(self._set_path_resolution)
        layout.addWidget(self.resolve_paths)
        layout.addSpacing(12)

        self.verbose = OptionWidget(
            text=strings.get("option.settings.verbose"),
            hint=strings.get("hint.settings.verbose"),
            checked=self.settings.verbose,
            icon=_icon("verbose"),
        )
        self.verbose.changed.connect(self._set_verbose)
        layout.addWidget(self.verbose)
        layout.addSpacing(12)

        self.remember_output = OptionWidget(
            text=strings.get("option.settings.remember_output"),
            hint=strings.get("hint.settings.remember_output"),
            checked=self.settings.remember_output,
            icon=_icon("remember_output"),
        )
        self.remember_output.changed.connect(self._set_output_memory)
        layout.addWidget(self.remember_output)
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
        resolver = game.resolve if self.settings.resolve_paths else game.Installation.from_root
        installation = resolver(source)

        if installation is None:
            self.root.invalid = True
            return

        self.root.invalid = False
        self.settings.game_root = installation.root
        if self.settings.resolve_paths:
            self.root.value = installation.root.as_posix()
        self.changed.emit()
        self.game_root_changed.emit()

    def _set_path_resolution(self, enabled: bool) -> None:
        self.settings.resolve_paths = enabled
        value = self.root.value.strip()
        root_changed = False

        if enabled and value:
            installation = game.resolve(Path(value))
            if installation is not None:
                self.root.invalid = False
                self.settings.game_root = installation.root
                self.root.value = installation.root.as_posix()
                root_changed = True

        self.changed.emit()
        if root_changed:
            self.game_root_changed.emit()
        self.path_resolution_changed.emit()

    def _set_verbose(self, enabled: bool) -> None:
        self.settings.verbose = enabled
        self.changed.emit()
        self.verbose_changed.emit(enabled)

    def _set_output_memory(self, enabled: bool) -> None:
        self.settings.remember_output = enabled
        self.changed.emit()
        self.output_memory_changed.emit(enabled)
