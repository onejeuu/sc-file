from dataclasses import dataclass
from pathlib import Path


@dataclass
class Asset:
    path: Path
    format: str


@dataclass
class Error:
    path: str
    error: str


@dataclass
class Result:
    format: str
    error: Error | None = None
