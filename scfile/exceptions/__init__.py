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
from .formats import (
    McsaCountsLimit,
    McsaDecodingError,
    McsaUnknownLinkCount,
    McsaUnsupportedVersion,
    Ms3dCountsLimit,
    Ms3dEncodingError,
    OlDecodingError,
    OlUnsupportedFourcc,
)


# TODO: update imports
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
    "McsaCountsLimit",
    "McsaDecodingError",
    "McsaUnknownLinkCount",
    "McsaUnsupportedVersion",
    "OlDecodingError",
    "OlUnsupportedFourcc",
    "Ms3dCountsLimit",
    "Ms3dEncodingError",
)
