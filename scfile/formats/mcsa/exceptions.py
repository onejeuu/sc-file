from dataclasses import dataclass

from scfile import exceptions


class McsaDecodingError(exceptions.FileError, exceptions.DecodingError):
    """Base exception for MCSA model related errors."""

    @property
    def prefix(self):
        return "Model"


@dataclass
class McsaVersionUnsupported(McsaDecodingError, exceptions.UnsupportedError):
    """Raised when attempting to parse unsupported model version."""

    version: float

    def __str__(self):
        return f"{super().__str__()} has unsupported version: {self.version}."
