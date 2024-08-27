from .base import ScFileException
from .basic import (
    FileBasicError,
    FileIsEmpty,
    FileNotFound,
    FileSignatureInvalid,
    FileStructureInvalid,
    FileSuffixUnsupported,
)
from .decode import FileDecodingError, FileParsingError, FileUnsupportedError
from .mcsa import (
    McsaCountsLimit,
    McsaDecodingError,
    McsaUnknownLinkCount,
    McsaUnsupportedVersion,
)
from .ol import OlDecodingError, OlUnsupportedFourcc


__all__ = (
    "ScFileException",
    "FileBasicError",
    "FileIsEmpty",
    "FileNotFound",
    "FileSignatureInvalid",
    "FileStructureInvalid",
    "FileSuffixUnsupported",
    "FileDecodingError",
    "FileParsingError",
    "FileUnsupportedError",
    "McsaCountsLimit",
    "McsaDecodingError",
    "McsaUnknownLinkCount",
    "McsaUnsupportedVersion",
    "OlDecodingError",
    "OlUnsupportedFourcc",
)
