from dataclasses import dataclass
from pathlib import Path

from scfile.io.types import PathLike

from .base import ScFileException


class BaseFileError(ScFileException):
    @property
    def prefix(self) -> str:
        return "File"

    def __str__(self):
        return f"{self.prefix}"


@dataclass
class FileError(BaseFileError):
    file: PathLike

    @property
    def path(self):
        return Path(self.file)

    def __str__(self):
        return f'{super().__str__()} "{self.path.as_posix()}"'


@dataclass
class FileNotFound(FileError):
    """Exception occurring when file not found or does not exists."""

    def __str__(self):
        return f"{super().__str__()} not found (not exists)."


@dataclass
class FileIsEmpty(FileError):
    """Exception occurring when file is empty."""

    def __str__(self):
        return f"{super().__str__()} is empty."


@dataclass
class FileSuffixUnsupported(FileError):
    """Exception occurring when file cannot be decoded or encoded."""

    def __str__(self):
        return f"{super().__str__()} with suffix '{self.path.suffix}' is unsupported."


@dataclass
class FileSignatureInvalid(FileError):
    """Exception occurring when file signature does not match file type."""

    read: bytes
    signature: bytes

    def __str__(self):
        return (
            f"{super().__str__()} has invalid signature - "
            f"'{self.read.hex().upper()}' != '{self.signature.hex().upper()}'. "
            "(File content doesn't match suffix)."
        )


@dataclass
class FileStructureInvalid(FileError):
    """Exception occurring when file does not hold expected number of bytes."""

    pos: int

    def __str__(self):
        return f"{super().__str__()} has invalid structure. Current position: {self.pos}."
