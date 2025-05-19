from dataclasses import dataclass

from scfile.exceptions import base, io


class OlDecodingError(io.FileError, base.ParsingError):
    """Base exception for OL texture related errors."""

    @property
    def prefix(self):
        return "Texture"


@dataclass
class OlUnsupportedFourcc(OlDecodingError, base.UnsupportedError):
    """Raised when texture contains unsupported FOURCC code."""

    fourcc: bytes

    def __str__(self):
        return f"{super().__str__()} has unsupported FOURCC (format): {self.fourcc}."
