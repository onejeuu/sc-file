"""
Exceptions of scfile package.
"""

from .base import ScFileException
from .core import FileDecodingError, FileParsingError, FileUnsupportedError
from .file import (
    BaseFileError,
    FileIsEmpty,
    FileNotFound,
    FileSignatureInvalid,
    FileStructureInvalid,
    FileSuffixUnsupported,
)


__all__ = (
    "ScFileException",
    "FileDecodingError",
    "FileParsingError",
    "FileUnsupportedError",
    "BaseFileError",
    "FileIsEmpty",
    "FileNotFound",
    "FileSignatureInvalid",
    "FileStructureInvalid",
    "FileSuffixUnsupported",
)
