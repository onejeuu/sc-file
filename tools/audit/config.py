import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import click

from tools.audit.consts import CONFIG, EXCLUDE, FORMATS, REPORTS, ROOT


@dataclass
class Config:
    path: Path
    formats: tuple[str, ...]
    exclude: tuple[str, ...]
    workers: int
    animation: bool
    reports: Path
    stats: bool

    @classmethod
    def load(
        cls,
        path: Path | None,
        formats: tuple[str, ...],
        workers: int | None,
        animation: bool | None,
        reports: Path | None,
        stats: bool | None,
    ) -> Self:
        stored = {}
        if CONFIG.exists():
            with CONFIG.open("rb") as file:
                stored = tomllib.load(file)

        path = path or stored.get("path")
        if path is None:
            raise click.UsageError(f"Missing path. Pass PATH or set it in '{CONFIG}'.")

        reports = Path(reports or stored.get("reports", REPORTS))
        if not reports.is_absolute():
            reports = ROOT / reports

        return cls(
            path=Path(path).resolve(),
            formats=tuple(formats or stored.get("formats") or FORMATS),
            exclude=tuple(
                "/" + item.lower().replace("\\", "/").lstrip("/") for item in (*EXCLUDE, *stored.get("exclude", ()))
            ),
            workers=workers if workers is not None else stored.get("workers", os.cpu_count() or 4),
            animation=animation if animation is not None else stored.get("animation", True),
            reports=reports.resolve(),
            stats=stats if stats is not None else stored.get("stats", False),
        )
