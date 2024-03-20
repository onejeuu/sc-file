from pathlib import Path

from scfile.types import PathLike

from .base import ScFileException


class FileBasicError(ScFileException):
    """Basic files exception. Occurring when file processing."""

    def __init__(self, path: PathLike):
        self.path = Path(path)

    @property
    def posix_path(self) -> str:
        return self.path.as_posix()

    def __str__(self):
        return f"File '{self.posix_path}'"


class FileNotFound(FileBasicError):
    """Exception occurring when file not found or does not exists."""

    def __str__(self):
        return f"{super().__str__()} not found (not exists)."


class FileTypeUnsupported(FileBasicError):
    """Exception occurring when file cannot be decoded or encoded."""

    def __str__(self):
        return f"{super().__str__()} with suffix '{self.path.suffix}' is unsupported."


class InvalidSignature(FileBasicError):
    """Exception occurring when file signature does not match file type."""

    def __init__(self, path: PathLike, readed: int, signature: int):
        self.path = Path(path)
        self.readed = readed
        self.signature = signature

    def __str__(self):
        return (
            f"{super().__str__()} has invalid signature - "
            f"{hex(self.readed)} != {hex(self.signature)}. "
            "(File suffix does not match file type)."
        )
