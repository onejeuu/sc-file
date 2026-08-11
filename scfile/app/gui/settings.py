from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QSettings

from scfile.app.consts import APPLICATION, ORGANIZATION


def _bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return default


@dataclass(slots=True)
class Settings:
    game_root: Path | None = None
    resolve_paths: bool = True
    verbose: bool = False
    remember_output: bool = False
    output: Path | None = None


class Store:
    def __init__(self, data: QSettings | None = None):
        self.data = data if data is not None else QSettings(ORGANIZATION, APPLICATION)

    def load(self) -> Settings:
        value = self.data.value("game/root", "")
        root = Path(str(value)) if value else None
        resolve_paths = _bool(self.data.value("paths/resolve", True), True)
        verbose = _bool(self.data.value("feedback/verbose", False), False)
        remember_output = _bool(self.data.value("convert/remember_output", False), False)
        value = self.data.value("convert/output", "")
        output = Path(str(value)) if value else None
        return Settings(
            game_root=root,
            resolve_paths=resolve_paths,
            verbose=verbose,
            remember_output=remember_output,
            output=output,
        )

    def save(self, settings: Settings) -> None:
        self.data.setValue("game/root", str(settings.game_root or ""))
        self.data.setValue("paths/resolve", settings.resolve_paths)
        self.data.setValue("feedback/verbose", settings.verbose)
        self.data.setValue("convert/remember_output", settings.remember_output)
        self.data.setValue("convert/output", str(settings.output or ""))
        self.data.sync()
