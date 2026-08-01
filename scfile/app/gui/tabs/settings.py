"""GUI settings tab."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from scfile.app.gui import game
from scfile.app.gui.settings import Settings, Store
from scfile.app.gui.shared import strings
from scfile.app.gui.shared.styles import Styles
from scfile.app.gui.widgets.option import OptionWidget
from scfile.app.gui.widgets.path import PathInputWidget


class SettingsTab(QWidget):
    root_changed = Signal()
    verbose_changed = Signal(bool)

    def __init__(self, settings: Settings, store: Store):
        super().__init__()
        self.settings = settings
        self.store = store
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)

        root_group = QWidget()
        root_layout = QVBoxLayout(root_group)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(4)

        root_label = QLabel(strings.get("label.settings.game_root"))
        root_label.setStyleSheet(Styles.LABEL)
        self.root = PathInputWidget(
            placeholder="C:/EXBO/runtime/stalcraft",
            caption=strings.get("dialog.settings.game_root"),
        )

        installation = game.resolve(self.settings.game_root or Path.home())
        if installation:
            self.settings.game_root = installation.root
            self.root.setText(installation.root.as_posix())
            self.store.save(self.settings)

        self.root.changed.connect(self._change_root)

        hint = QLabel(strings.get("hint.settings.game_root"))
        hint.setStyleSheet(Styles.HINT)
        hint.setWordWrap(True)

        self.resolve_paths = OptionWidget(
            text=strings.get("option.settings.resolve_paths"),
            hint=strings.get("hint.settings.resolve_paths"),
            checked=self.settings.resolve_paths,
        )
        self.resolve_paths.changed.connect(self._change_resolve_paths)

        root_layout.addWidget(root_label)
        root_layout.addWidget(self.root)
        root_layout.addWidget(hint)

        layout.addWidget(root_group)
        layout.addSpacing(12)
        layout.addWidget(self.resolve_paths)
        layout.addSpacing(12)

        self.verbose = OptionWidget(
            text=strings.get("option.settings.verbose"),
            hint=strings.get("hint.settings.verbose"),
            checked=self.settings.verbose,
        )
        self.verbose.changed.connect(self._change_verbose)
        layout.addWidget(self.verbose)
        layout.addStretch()

    def _change_root(self, value: str) -> None:
        path = value.strip()
        if not path:
            self.root.invalid = False
            self.settings.game_root = None
            self.store.save(self.settings)
            self.root_changed.emit()
            return

        source = Path(path)
        if self.settings.resolve_paths:
            installation = game.resolve(source)
        elif game.is_root(source):
            installation = game.Installation(source.resolve())
        else:
            installation = None

        if installation is None:
            self.root.invalid = True
            return

        self.root.invalid = False
        self.settings.game_root = installation.root
        if self.settings.resolve_paths:
            self.root.setText(installation.root.as_posix())
        self.store.save(self.settings)
        self.root_changed.emit()

    def _change_resolve_paths(self, enabled: bool) -> None:
        self.settings.resolve_paths = enabled
        self.store.save(self.settings)
        if enabled:
            self._change_root(self.root.text())

    def _change_verbose(self, enabled: bool) -> None:
        self.settings.verbose = enabled
        self.store.save(self.settings)
        self.verbose_changed.emit(enabled)
