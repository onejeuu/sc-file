from dataclasses import dataclass


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
