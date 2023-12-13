from .base import ScFileException
from .basic import ScFileBasicError, SourceFileNotFound, UnsupportedSuffix, FileIsEmpty, InvalidSignature
from .convert import FileConvertingError, FileParsingError, FileUnsupportedError
from .mcsa import McsaFileError, McsaCountsLimit, McsaUnsupportedVersion, McsaUnsupportedFlags, McsaUnknownLinkCount
from .ol import OlFileError, OlUnknownFourcc, OlInvalidFormat, OlDXNError, OlDXNSize, OlDXNNotSquare
