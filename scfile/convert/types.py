"""File conversion result types."""

from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path


class Status(StrEnum):
    """File conversion outcome."""

    WRITTEN = auto()
    SKIPPED = auto()


@dataclass(frozen=True, slots=True)
class Output:
    """Output path and conversion outcome."""

    path: Path
    status: Status
