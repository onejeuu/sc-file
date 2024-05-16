from pathlib import Path

from scfile.utils.types import PathLike

from .decode import FileDecodingError, FileParsingError, FileUnsupportedError


class McsaDecodingError(FileDecodingError):
    """Base mcsa model file exception."""

    def __str__(self):
        return f"Model '{self.posix_path}'"


class McsaCountsLimit(McsaDecodingError, FileParsingError):
    """Exception occurring when model counts is not read correctly."""

    def __init__(self, path: PathLike, counts: int):
        self.path = Path(path)
        self.counts = counts

    def __str__(self):
        return f"{super().__str__()} has invalid format."


class McsaUnknownLinkCount(McsaDecodingError, FileParsingError):
    """Exception occurring when model skeleton bones have unknown link count."""

    def __init__(self, path: PathLike, link_count: int):
        self.path = Path(path)
        self.link_count = link_count

    def __str__(self):
        return f"{super().__str__()} has unknown bones link count: {self.link_count}"


class McsaUnsupportedVersion(McsaDecodingError, FileUnsupportedError):
    """Exception occurring when model version unsupported."""

    def __init__(self, path: PathLike, version: float):
        self.path = Path(path)
        self.version = version

    def __str__(self):
        return f"{super().__str__()} has unsupported version: {self.version}"
