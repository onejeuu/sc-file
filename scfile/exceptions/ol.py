from dataclasses import dataclass

from .decode import FileDecodingError, FileUnsupportedError


class OlDecodingError(FileDecodingError):
    """Base exception for texture files."""

    @property
    def prefix(self):
        return "Texture"


@dataclass
class OlUnsupportedFourcc(OlDecodingError, FileUnsupportedError):
    """Exception occurring when texture have unsupported or unknown fourcc."""

    fourcc: str

    def __str__(self):
        return f"{super().__str__()} has unsupported format: '{self.fourcc}'."
