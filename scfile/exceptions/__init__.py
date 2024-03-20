from .base import ScFileException
from .basic import (
    FileBasicError,
    FileNotFound,
    FileSuffixUnsupported,
    FileSignatureInvalid,
)
from .decode import FileDecodingError, FileParsingError, FileUnsupportedError
from .mcsa import (
    McsaDecodingError,
    McsaCountsLimit,
    McsaUnsupportedVersion,
    McsaUnknownLinkCount,
)
from .ol import OlDecodingError, OlUnknownFourcc, OlInvalidFormat
