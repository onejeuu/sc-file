from .base import ScFileException
from .basic import (
    FileBasicError,
    FileNotFound,
    FileSignatureInvalid,
    FileSuffixUnsupported,
)
from .decode import FileDecodingError, FileParsingError, FileUnsupportedError
from .mcsa import (
    McsaCountsLimit,
    McsaDecodingError,
    McsaUnknownLinkCount,
    McsaUnsupportedVersion,
)
from .ol import OlDecodingError, OlUnknownFourcc


__all__ = (
    "ScFileException",
    "FileBasicError",
    "FileNotFound",
    "FileSuffixUnsupported",
    "FileSignatureInvalid",
    "FileDecodingError",
    "FileParsingError",
    "FileUnsupportedError",
    "McsaCountsLimit",
    "McsaDecodingError",
    "McsaUnknownLinkCount",
    "McsaUnsupportedVersion",
    "OlDecodingError",
    "OlUnknownFourcc",
)
