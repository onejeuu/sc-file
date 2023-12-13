from pathlib import Path

from scfile.consts import PathLike

from .convert import FileConvertingError, FileParsingError, FileUnsupportedError


class OlFileError(FileConvertingError):
    """Base ol texture file exception."""

    def __str__(self):
        return f"Texture '{self.posix_path}'"

class OlInvalidFormat(OlFileError, FileParsingError):
    """Exception occurring when cannot uncompress image."""

    def __str__(self):
        return f"{super().__str__()} has invalid format."

class OlUnknownFourcc(OlFileError, FileUnsupportedError):
    """Exception occurring when texture have unknown fourcc."""

    def __init__(self, path: PathLike, fourcc: str):
        self.path = Path(path)
        self.fourcc = fourcc

    def __str__(self):
        return f"{super().__str__()} has unknown format '{self.fourcc}'"

class OlDXNError(OlFileError, FileParsingError):
    """Exception occurring due DXN XY unpacking."""
    pass

class OlDXNSize(OlDXNError):
    pass

class OlDXNNotSquare(OlDXNError):
    pass
