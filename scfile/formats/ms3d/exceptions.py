from dataclasses import dataclass

from scfile.exceptions import core


class Ms3dEncodingError(core.FileEncodingError):
    """Base exception for ms3d files."""

    @property
    def prefix(self):
        return "MS3D (MilkShape 3D)"


@dataclass
class Ms3dCountsLimit(Ms3dEncodingError, core.FileUnsupportedError):
    """Exception occurring when model counts is too big."""

    name: str
    counts: int
    limit: int

    def __str__(self):
        return f"{super().__str__()} count of {self.name} exceeds limit ({self.counts:,} > {self.limit:,})."
