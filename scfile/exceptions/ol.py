from pathlib import Path

from scfile.types import PathLike

from .decode import FileDecodingError, FileParsingError, FileUnsupportedError


class OlDecodingError(FileDecodingError):
    """Base ol texture file exception."""

    def __str__(self):
        return f"Texture '{self.posix_path}'"


class OlInvalidFormat(OlDecodingError, FileParsingError):
    """Exception occurring when cannot decompress image."""

    def __str__(self):
        return f"{super().__str__()} has invalid format."


class OlUnknownFourcc(OlDecodingError, FileUnsupportedError):
    """Exception occurring when texture have unknown fourcc."""

    def __init__(self, path: PathLike, fourcc: str):
        self.path = Path(path)
        self.fourcc = fourcc

    def __str__(self):
        return f"{super().__str__()} has unknown format '{self.fourcc}'"
