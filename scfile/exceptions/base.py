"""
Base exceptions.
"""

from dataclasses import dataclass
from pathlib import Path

from scfile.core.types import PathLike


class ScFileException(Exception):
    """Base exception for scfile library."""

    pass


class DecodingError(ScFileException):
    """Base exception occurring while file decoding."""

    pass


class EncodingError(ScFileException):
    """Base exception occurring while file encoding."""

    pass


class ParsingError(ScFileException):
    """Base exception occurring due to unexpected file structure."""

    pass


class UnsupportedError(ScFileException):
    """Base exception occurring intentionally for unsupported formats."""

    pass


class BaseIOError(ScFileException):
    """Base exception occurring i/o operations."""

    @property
    def prefix(self) -> str:
        return "File"

    def __str__(self):
        return f"{self.prefix}"


@dataclass
class FileError(BaseIOError):
    """Base exception occurring file i/o operations."""

    file: PathLike

    @property
    def path(self):
        return Path(self.file)

    def __str__(self):
        return f"{super().__str__()} '{self.path.as_posix()}'"
