from dataclasses import dataclass

from scfile.exceptions import core


class McsaDecodingError(core.FileDecodingError):
    """Base exception for model files."""

    @property
    def prefix(self):
        return "Model"


@dataclass
class McsaCountsLimit(McsaDecodingError, core.FileParsingError):
    """Exception occurring when model counts is not read correctly."""

    counts: int

    def __str__(self):
        return f"{super().__str__()} has invalid structure. Model cannot have {self.counts:,} vertices/polygons."


@dataclass
class McsaUnknownLinkCount(McsaDecodingError, core.FileParsingError):
    """Exception occurring when model skeleton bones have unknown link count."""

    link_count: int

    def __str__(self):
        return f"{super().__str__()} has unknown bones link count: {self.link_count}."


@dataclass
class McsaUnsupportedVersion(McsaDecodingError, core.FileUnsupportedError):
    """Exception occurring when model version unsupported."""

    version: float

    def __str__(self):
        return f"{super().__str__()} has unsupported version: {self.version}."
