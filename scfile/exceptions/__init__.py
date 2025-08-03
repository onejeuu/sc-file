"""
Exceptions of scfile package.
"""

from .base import ScFileException, DecodingError, EncodingError, ParsingError, UnsupportedError, BaseIOError, FileError
from .file import FileNotFound, EmptyFileError, UnsupportedFormatError, InvalidSignatureError, InvalidStructureError

__all__ = (
    "ScFileException",
    "DecodingError",
    "EncodingError",
    "ParsingError",
    "UnsupportedError",
    "BaseIOError",
    "FileError",
    "FileNotFound",
    "EmptyFileError",
    "UnsupportedFormatError",
    "InvalidSignatureError",
    "InvalidStructureError",
)
