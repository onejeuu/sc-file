from .base import ScFileException
from .file import BaseFileError


class FileDecodingError(BaseFileError):
    """Base exception occurring while file decoding."""

    pass


class FileParsingError(ScFileException):
    """Base exception occurring due to unexpected file structure."""

    pass


class FileUnsupportedError(ScFileException):
    """Base exception occurring intentionally for unsupported formats."""

    pass
