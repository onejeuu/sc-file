from dataclasses import dataclass

from scfile import exceptions
from scfile.consts import McsaModel


class McsaDecodingError(exceptions.FileError, exceptions.DecodingError):
    """Base exception for MCSA model related errors."""

    @property
    def prefix(self):
        return "Model"


@dataclass
class McsaCountsLimit(McsaDecodingError, exceptions.ParsingError):
    """Raised when model exceeds allowed geometry limits (vertices/polygons count)."""

    type: str
    count: int

    def __str__(self) -> str:
        return (
            f"{super().__str__()} has invalid structure - "
            f"{self.count:,} {self.type} "
            f"(max reasonable: {McsaModel.GEOMETRY_LIMIT:,})."
        )


@dataclass
class McsaBoneLinksError(McsaDecodingError, exceptions.ParsingError):
    """Raised when mesh contain unexpected/invalid links count."""

    links_count: int

    def __str__(self):
        return f"{super().__str__()} has unexpected links count: {self.links_count}."


@dataclass
class McsaVersionUnsupported(McsaDecodingError, exceptions.UnsupportedError):
    """Raised when attempting to parse unsupported model version."""

    version: float

    def __str__(self):
        return f"{super().__str__()} has unsupported version: {self.version}."
