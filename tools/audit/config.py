import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import click

from scfile.convert import decoders


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "audit.toml"
LOGS = ROOT / "errors.jsonl"

DECODERS = decoders()
FORMATS = tuple(sorted(DECODERS))


@dataclass
class Config:
    path: Path
    formats: tuple[str, ...]
    workers: int
    animation: bool
    log: Path

    @classmethod
    def load(
        cls,
        path: Path | None,
        formats: tuple[str, ...],
        workers: int | None,
        animation: bool | None,
        log: Path | None,
    ) -> Self:
        stored = {}
        if CONFIG.exists():
            with CONFIG.open("rb") as file:
                stored = tomllib.load(file)

        path = path or stored.get("path")
        if path is None:
            raise click.UsageError(f"Missing path. Pass PATH or set it in '{CONFIG}'.")

        log = Path(log or stored.get("log", LOGS))
        if not log.is_absolute():
            log = ROOT / log

        return cls(
            path=Path(path).resolve(),
            formats=tuple(formats or stored.get("formats") or FORMATS),
            workers=workers if workers is not None else stored.get("workers", os.cpu_count() or 4),
            animation=animation if animation is not None else stored.get("animation", True),
            log=log.resolve(),
        )
