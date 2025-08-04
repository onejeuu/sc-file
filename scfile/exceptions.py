import pathlib
from dataclasses import dataclass
from typing import Optional

from scfile.types import PathLike


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
    def path(self) -> pathlib.Path:
        return pathlib.Path(self.file)

    def __str__(self):
        return f"{super().__str__()} '{self.path.as_posix()}'"


@dataclass
class FileNotFound(FileError):
    """Raised when file doesn't exist."""

    def __str__(self):
        return f"{super().__str__()} not found or doesn't exist."


@dataclass
class EmptyFileError(FileError):
    """Raised when file is empty."""

    def __str__(self):
        return f"{super().__str__()} is empty."


@dataclass
class UnsupportedFormatError(FileError):
    """Raised when file format (by suffix) is not supported."""

    def __str__(self):
        return f"{super().__str__()} has unsupported suffix '{self.path.suffix}'."


@dataclass
class InvalidSignatureError(FileError):
    """Raised when file signature doesn't match expected."""

    actual: bytes
    expected: bytes

    def __str__(self):
        return (
            f"{super().__str__()} has invalid signature - "
            f"'{self.actual.hex().upper()}' != '{self.expected.hex().upper()}'. "
            "(file suffix doesn't match file content)."
        )


@dataclass
class InvalidStructureError(FileError):
    """Raised when file structure is invalid."""

    position: Optional[int] = None

    def __str__(self):
        return f"{super().__str__()} parsing failed{f' at position {self.position}' if self.position else ''}."
