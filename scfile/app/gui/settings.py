from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QSettings

from scfile.app.consts import APPLICATION, DEFAULT_OUTPUT, ORGANIZATION


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
    export_path: Path = DEFAULT_OUTPUT


class Store:
    def __init__(self, data: QSettings | None = None):
        self.data = data if data is not None else QSettings(ORGANIZATION, APPLICATION)

    def load(self) -> Settings:
        value = self.data.value("game/root", "")
        root = Path(str(value)) if value else None
        resolve_paths = _bool(self.data.value("paths/resolve", True), True)
        verbose = _bool(self.data.value("feedback/verbose", False), False)
        value = self.data.value("convert/output", "")
        export_path = Path(str(value)) if value else DEFAULT_OUTPUT
        return Settings(
            game_root=root,
            resolve_paths=resolve_paths,
            verbose=verbose,
            export_path=export_path,
        )

    def save(self, settings: Settings) -> None:
        self.data.setValue("game/root", str(settings.game_root or ""))
        self.data.setValue("paths/resolve", settings.resolve_paths)
        self.data.setValue("feedback/verbose", settings.verbose)
        self.data.setValue("convert/output", str(settings.export_path))
        self.data.remove("convert/remember_output")
        self.data.remove("convert/last_output")
        self.data.sync()
