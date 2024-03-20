from .base import ScFileException
from .basic import (
    FileBasicError,
    FileNotFound,
    FileTypeUnsupported,
    InvalidSignature,
)
from .decode import FileDecodingError, FileParsingError, FileUnsupportedError
from .mcsa import (
    McsaDecodingError,
    McsaCountsLimit,
    McsaUnsupportedVersion,
    McsaUnknownLinkCount,
)
from .ol import OlDecodingError, OlUnknownFourcc, OlInvalidFormat
