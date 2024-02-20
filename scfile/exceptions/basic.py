from pathlib import Path

from scfile.types import PathLike

from .base import ScFileException


class ScFileBasicError(ScFileException):
    """Basic files exception. Occurring when file processing."""

    def __init__(self, path: PathLike):
        self.path = Path(path)

    @property
    def posix_path(self) -> str:
        return self.path.as_posix()

    def __str__(self):
        return f"File '{self.posix_path}'"

class SourceFileNotFound(ScFileBasicError):
    """Exception occurring when source (encrypted) file not found or does not exists."""

    def __str__(self):
        return f"{super().__str__()} not found (not exists)."

class UnsupportedSuffix(ScFileBasicError):
    """Exception occurring when file have unknown suffix."""

    def __str__(self):
        return f"{super().__str__()} with suffix '{self.path.suffix}' is unsupported."

class FileIsEmpty(ScFileBasicError):
    """Exception occurring when file is empty."""

    def __str__(self):
        return f"{super().__str__()} is empty."

class InvalidSignature(ScFileBasicError):
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
