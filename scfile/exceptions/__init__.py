from .base import ScFileException
from .decode import FileDecodingError, FileParsingError, FileUnsupportedError
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
    OlDecodingError,
    OlUnsupportedFourcc,
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
    "McsaCountsLimit",
    "McsaDecodingError",
    "McsaUnknownLinkCount",
    "McsaUnsupportedVersion",
    "OlDecodingError",
    "OlUnsupportedFourcc",
)
