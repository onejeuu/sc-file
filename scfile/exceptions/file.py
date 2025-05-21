"""
File validation exceptions.
"""

from dataclasses import dataclass
from typing import Optional

from .base import FileError


@dataclass
class FileNotFound(FileError):
    """Raised when file not found or doesn't exist."""

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
