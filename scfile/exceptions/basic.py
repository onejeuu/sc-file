from dataclasses import dataclass
from pathlib import Path

from scfile.utils.types import PathLike

from .base import ScFileException


@dataclass
class FileBasicError(ScFileException):
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
class FileNotFound(FileBasicError):
    """Exception occurring when file not found or does not exists."""

    def __str__(self):
        return f"{super().__str__()} not found (not exists)."


@dataclass
class FileIsEmpty(FileBasicError):
    """Exception occurring when file is empty."""

    def __str__(self):
        return f"{super().__str__()} is empty."


@dataclass
class FileSuffixUnsupported(FileBasicError):
    """Exception occurring when file cannot be decoded or encoded."""

    def __str__(self):
        return f"{super().__str__()} with suffix '{self.path.suffix}' is unsupported."


@dataclass
class FileSignatureInvalid(FileBasicError):
    """Exception occurring when file signature does not match file type."""

    readed: int
    signature: int

    def __str__(self):
        return (
            f"{super().__str__()} has invalid signature - "
            f"{hex(self.readed)} != {hex(self.signature)}. "
            "(File suffix does not match file type)."
        )


@dataclass
class FileStructureInvalid(FileBasicError):
    """Exception occurring when file does not hold expected number of bytes."""

    pos: int

    def __str__(self):
        return f"{super().__str__()} has invalid structure. Current position: {self.pos}."
