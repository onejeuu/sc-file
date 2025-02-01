from .base import ScFileException
from .file import BaseFileError, FileError


class FileDecodingError(FileError):
    """Base exception occurring while file decoding."""

    pass


class FileEncodingError(BaseFileError):
    """Base exception occurring while file encoding."""

    pass


class FileParsingError(ScFileException):
    """Base exception occurring due to unexpected file structure."""

    pass


class FileUnsupportedError(ScFileException):
    """Base exception occurring intentionally for unsupported formats."""

    pass
