from dataclasses import dataclass

from scfile.exceptions import core


class OlDecodingError(core.FileDecodingError):
    """Base exception for texture files."""

    @property
    def prefix(self):
        return "Texture"


@dataclass
class OlUnsupportedFourcc(OlDecodingError, core.FileUnsupportedError):
    """Exception occurring when texture have unsupported or unknown fourcc."""

    fourcc: bytes

    def __str__(self):
        return f"{super().__str__()} has unsupported format: {self.fourcc}."
