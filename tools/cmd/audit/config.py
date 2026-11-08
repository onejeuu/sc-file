import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from scfile import formats
from tools.paths import ROOT


CONFIG = ROOT / "configs" / "audit" / "config.toml"
FORMATS = tuple(sorted(str(format) for format in formats.registry.decoders))


@dataclass(frozen=True)
class Settings:
    root: Path
    formats: tuple[str, ...]
    relations: tuple[str, ...]
    exclude: tuple[str, ...]
    workers: int
    animation: bool
    extended_chunk: bool
    stats: bool


def read() -> dict[str, Any]:
    try:
        with CONFIG.open("rb") as file:
            return tomllib.load(file)

    except (FileNotFoundError, OSError, tomllib.TOMLDecodeError) as error:
        if not isinstance(error, FileNotFoundError):
            raise click.UsageError(f"Cannot read audit config '{CONFIG}': {error}") from None
        return {}


def resolve(
    path: Path | None,
    selected_formats: tuple[str, ...],
    selected_relations: tuple[str, ...],
    workers: int | None,
    animation: bool | None,
    extended_chunk: bool | None,
    stats: bool | None,
) -> Settings:
    values = read()
    source = path or values.get("path")
    if source is None:
        raise click.UsageError(f"Missing path. Pass PATH or set it in '{CONFIG}'.")

    match selected_formats, selected_relations:
        case (), ():
            chosen_formats = tuple(values.get("formats") or FORMATS)
            chosen_relations = tuple(values.get("relations") or ())
        case _:
            chosen_formats = selected_formats
            chosen_relations = selected_relations

    configured_workers = workers if workers is not None else values.get("workers", os.cpu_count() or 4)
    if isinstance(configured_workers, bool) or not isinstance(configured_workers, int) or configured_workers < 0:
        raise click.UsageError("workers must be a non-negative integer")

    return Settings(
        root=Path(source).resolve(),
        formats=chosen_formats,
        relations=chosen_relations,
        exclude=tuple(path.casefold().replace("\\", "/").lstrip("/") for path in values.get("exclude", ())),
        workers=configured_workers,
        animation=animation if animation is not None else values.get("animation", True),
        extended_chunk=extended_chunk if extended_chunk is not None else values.get("extended_chunk", False),
        stats=stats if stats is not None else values.get("stats", False),
    )
