from dataclasses import dataclass

from scfile.exceptions import base


class Ms3dEncodingError(base.BaseIOError, base.EncodingError):
    """Base exception for MS3D model related errors."""

    @property
    def prefix(self):
        return "MS3D Model"


@dataclass
class Ms3dCountsLimit(Ms3dEncodingError, base.UnsupportedError):
    """Raised when model exceeds format limitations."""

    type: str
    count: int
    limit: int

    def __str__(self) -> str:
        return f"{super().__str__()} - {self.type} count exceeds limit: {self.count:,} > {self.limit:,}"
