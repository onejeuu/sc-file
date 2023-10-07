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

class OlUnsupportedFormat(OlFileError):
    pass

class OlUnpackingError(OlFileError):
    pass


# * .mcsa files
class McsaFileError(ScFileException):
    pass

class McsaStringError(McsaFileError):
    pass

class McsaUnsupportedVersion(McsaFileError):
    pass

class McsaUnsupportedFlags(McsaFileError):
    pass

class McsaUnsupportedLinkCount(McsaFileError):
    pass
