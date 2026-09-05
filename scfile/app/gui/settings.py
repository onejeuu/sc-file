import os
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QSettings

from scfile.app.consts import APPLICATION, DEFAULT_OUTPUT, ORGANIZATION
from scfile.app.gui import strings
from scfile.app.localization import Lang, system_language


def _bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return default


def _workers(value: object) -> int:
    if isinstance(value, (int, str)):
        try:
            return max(1, min(99, int(value)))
        except ValueError:
            pass

    return min(99, os.cpu_count() or 4)


@dataclass(slots=True)
class Settings:
    resolve_paths: bool = True
    verbose: bool = False
    game_root: Path | None = None
    export_path: Path = DEFAULT_OUTPUT
    workers: int = field(default_factory=lambda: min(99, os.cpu_count() or 4))
    language: Lang = field(default_factory=system_language)


class Store:
    def __init__(self, data: QSettings | None = None):
        self.data = data if data is not None else QSettings(ORGANIZATION, APPLICATION)

    def load(self) -> Settings:
        language = self._load_language()
        workers = _workers(self.data.value("performance/workers"))

        value = self.data.value("paths/game", "")
        game_root = Path(str(value)) if value else None

        resolve_paths = _bool(self.data.value("general/resolve", True), True)
        verbose = _bool(self.data.value("general/verbose", False), False)

        value = self.data.value("paths/export", "")
        export_path = Path(str(value)) if value else DEFAULT_OUTPUT

        return Settings(
            workers=workers,
            language=language,
            game_root=game_root,
            resolve_paths=resolve_paths,
            verbose=verbose,
            export_path=export_path,
        )

    def save(self, settings: Settings) -> None:
        self.data.setValue("performance/workers", _workers(settings.workers))
        self.data.setValue("interface/language", settings.language)
        self.data.setValue("paths/game", str(settings.game_root or ""))
        self.data.setValue("general/resolve", settings.resolve_paths)
        self.data.setValue("general/verbose", settings.verbose)
        self.data.setValue("paths/export", str(settings.export_path))
        self.data.sync()

    def _load_language(self) -> Lang:
        value = self.data.value("interface/language")
        for language in strings.DATA:
            if value == language:
                return language

        language = system_language()
        self.data.setValue("interface/language", language)
        self.data.sync()
        return language
