class ScFileException(Exception):
    pass


class SourceFileNotFound(ScFileException):
    pass

class UnsupportedFormat(ScFileException):
    pass

class InvalidSignature(ScFileException):
    pass

class FileIsEmpty(ScFileException):
    pass


class OlFileError(ScFileException):
    pass

class OlUnpackingError(OlFileError):
    pass

class OlUnknownFormat(OlFileError):
    pass


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
