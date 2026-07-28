from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from tools.cmd.audit.schemas import Record


@dataclass(slots=True)
class Asset:
    path: str
    format: str


@dataclass(slots=True)
class Error:
    path: str
    error: str


@dataclass(slots=True)
class Result:
    format: str
    error: Error | None = None
    records: list[Record] | None = None


@dataclass(slots=True)
class Relations:
    hands: Path | None
    arms: list[Path]
    face: list[Path]
    heads: list[Path]
    body: list[Path]
    models: list[Path]
