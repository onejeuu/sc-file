from dataclasses import dataclass
from pathlib import Path

from scfile.io.types import PathLike

from .base import ScFileException


@dataclass
class BaseFileError(ScFileException):
    """Basic files exception. Occurring with file processing."""

    file: PathLike

    @property
    def path(self):
        return Path(self.file)

    @property
    def prefix(self) -> str:
        return "File"

    def __str__(self):
        return f'{self.prefix} "{self.path.as_posix()}"'


@dataclass
class FileNotFound(BaseFileError):
    """Exception occurring when file not found or does not exists."""

    def __str__(self):
        return f"{super().__str__()} not found (not exists)."


@dataclass
class FileIsEmpty(BaseFileError):
    """Exception occurring when file is empty."""

    def __str__(self):
        return f"{super().__str__()} is empty."


@dataclass
class FileSuffixUnsupported(BaseFileError):
    """Exception occurring when file cannot be decoded or encoded."""

    def __str__(self):
        return f"{super().__str__()} with suffix '{self.path.suffix}' is unsupported."


@dataclass
class FileSignatureInvalid(BaseFileError):
    """Exception occurring when file signature does not match file type."""

    readed: bytes
    signature: bytes

    def __str__(self):
        return (
            f"{super().__str__()} has invalid signature - "
            f"'{self.readed.hex().upper()}' != '{self.signature.hex().upper()}'. "
            "(File content doesnt match suffix)."
        )


@dataclass
class FileStructureInvalid(BaseFileError):
    """Exception occurring when file does not hold expected number of bytes."""

    pos: int

    def __str__(self):
        return f"{super().__str__()} has invalid structure. Current position: {self.pos}."
