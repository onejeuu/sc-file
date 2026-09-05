from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app import files
from scfile.app.consts import DEFAULT_OUTPUT
from scfile.app.game import GameRoot
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.widgets.card import CardWidget
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathInputWidget


ICON_SIZE = QSize(22, 22)


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
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(16)

        title = QLabel(strings.get("tab.settings"))
        title.setStyleSheet(Styles.TITLE)
        layout.addWidget(title)

        general = CardWidget(strings.get("label.settings.general"))
        general.content.setSpacing(16)

        self.resolve_paths = OptionWidget(
            text=strings.get("option.settings.resolve"),
            hint=strings.get("option.settings.resolve.hint"),
            checked=self.settings.resolve_paths,
            icon=_icon("resolve_paths"),
        )
        self.resolve_paths.changed.connect(self._set_path_resolution)
        general.content.addWidget(self.resolve_paths)

        self.verbose = OptionWidget(
            text=strings.get("option.settings.verbose"),
            hint=strings.get("option.settings.verbose.hint"),
            checked=self.settings.verbose,
            icon=_icon("verbose"),
        )
        self.verbose.changed.connect(self._set_verbose)
        general.content.addWidget(self.verbose)
        layout.addWidget(general)

        paths = CardWidget(strings.get("label.settings.paths"))
        paths.content.setSpacing(16)
        self.root = PathInputWidget(
            placeholder="C:/EXBO/runtime/stalcraft",
            caption=strings.get("dialog.settings.game"),
        )
        if self.settings.game_root is not None:
            self.root.value = self.settings.game_root.as_posix()
        self.root.changed.connect(self._set_game_root)

        self.export = PathInputWidget(
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.settings.export"),
        )
        self.export.value = self.settings.export_path.as_posix()
        self.export.changed.connect(self._set_export_path)

        paths.content.addWidget(
            self._path_setting(
                "gameroot",
                strings.get("label.settings.game"),
                strings.get("label.settings.game.hint"),
                self.root,
            )
        )
        paths.content.addWidget(
            self._path_setting(
                "export_path",
                strings.get("label.settings.export"),
                strings.get("label.settings.export.hint"),
                self.export,
            )
        )
        layout.addWidget(paths)
        layout.addStretch()

    def _path_setting(self, icon: str, title: str, hint: str, field: PathInputWidget) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        image = QLabel()
        image.setPixmap(_icon(icon).pixmap(ICON_SIZE))
        layout.addWidget(image, 0, Qt.AlignmentFlag.AlignTop)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(3)
        label = QLabel(title)
        label.setStyleSheet(Styles.LABEL)
        content.addWidget(label)
        description = QLabel(hint)
        description.setStyleSheet(Styles.DESCRIPTION)
        content.addWidget(description)
        content.addSpacing(5)
        content.addWidget(field)
        layout.addLayout(content, 1)
        return widget

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
