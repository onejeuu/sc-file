from pathlib import Path

from scfile.consts import PathLike
from scfile.utils.mcsa.flags import McsaFlags

from .convert import FileConvertingError, FileParsingError, FileUnsupportedError


class McsaFileError(FileConvertingError):
    """Base mcsa model file exception."""

    def __str__(self):
        return f"Model '{self.posix_path}'"

class McsaCountsLimit(McsaFileError, FileParsingError):
    """Exception occurring when vertices or polygons count is not read correctly."""

    def __init__(self, path: PathLike, counts: int):
        self.path = Path(path)
        self.counts = counts

    def __str__(self):
        return f"{super().__str__()} has invalid format."

class McsaUnknownLinkCount(McsaFileError, FileParsingError):
    """Exception occurring when model skeleton bones have unknown link count."""

    def __init__(self, path: PathLike, link_count: int):
        self.path = Path(path)
        self.link_count = link_count

    def __str__(self):
        return f"{super().__str__()} has unknown bones link count: {self.link_count}"

class McsaUnsupportedVersion(McsaFileError, FileUnsupportedError):
    """Exception occurring when model version unsupported."""

    def __init__(self, path: PathLike, version: float):
        self.path = Path(path)
        self.version = version

    def __str__(self):
        return f"{super().__str__()} has unsupported version: {self.version}"

class McsaUnsupportedFlags(McsaFileError, FileUnsupportedError):
    """Exception occurring when model flags unsupported."""

    def __init__(self, path: PathLike, flags: McsaFlags):
        self.path = Path(path)
        self.flags = flags

    def __str__(self):
        return f"{super().__str__()} has unsupported flags: {self.flags}"
