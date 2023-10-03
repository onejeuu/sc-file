class ScFileException(Exception):
    pass


# * basic
class SourceFileNotFound(ScFileException):
    pass

class UnsupportedFormat(ScFileException):
    pass

class InvalidSignature(ScFileException):
    pass

class FileIsEmpty(ScFileException):
    pass


# * .ol files
class OlFileError(ScFileException):
    pass

class OlUnpackingError(OlFileError):
    pass

class OlUnknownFormat(OlFileError):
    pass


# * .mcsa files
class McsaFileError(ScFileException):
    pass

class McsaStringError(McsaFileError):
    pass

class McsaUnknownVersion(McsaFileError):
    pass

class McsaUnsupportedFlags(McsaFileError):
    pass

class McsaUnsupportedLinkCount(McsaFileError):
    pass
