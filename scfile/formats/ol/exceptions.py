from dataclasses import dataclass

from scfile.exceptions import base


class OlDecodingError(base.FileError, base.ParsingError):
    """Base exception for OL texture related errors."""

    @property
    def prefix(self):
        return "Texture"


@dataclass
class OlFormatUnsupported(OlDecodingError, base.UnsupportedError):
    """Raised when texture contains unsupported format."""

    format: bytes

    def __str__(self):
        return f"{super().__str__()} has unsupported format: {self.format}."
