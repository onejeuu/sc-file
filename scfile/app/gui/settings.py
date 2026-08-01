"""Persistent GUI settings."""

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QSettings


@dataclass(slots=True)
class Settings:
    """User preferences retained between GUI sessions."""

    game_root: Path | None = None
    resolve_paths: bool = True


class Store:
    """Version-tolerant storage for GUI settings."""

    def __init__(self, data: QSettings | None = None):
        self.data = data if data is not None else QSettings("onejeuu", "scfile")

    @staticmethod
    def _bool(value: object, default: bool) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "on"}
        return default

    def load(self) -> Settings:
        """Load known settings while ignoring unknown keys."""

        value = self.data.value("game/root", "")
        root = Path(str(value)) if value else None
        resolve_paths = self._bool(self.data.value("paths/resolve", True), True)
        return Settings(game_root=root, resolve_paths=resolve_paths)

    def save(self, settings: Settings) -> None:
        """Persist the current settings."""

        self.data.setValue("game/root", str(settings.game_root or ""))
        self.data.setValue("paths/resolve", settings.resolve_paths)
        self.data.sync()
