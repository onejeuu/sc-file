class ScFileException(Exception):
    pass


class InvalidSignature(ScFileException):
    pass

class FileIsEmpty(ScFileException):
    pass


class OlFileError(ScFileException):
    pass

class UnpackingError(OlFileError):
    pass

class UnknownFormat(OlFileError):
    pass


class McsaFileError(ScFileException):
    pass

class UnknownVersion(McsaFileError):
    pass

class UnsupportedFlags(McsaFileError):
    pass

class UnsupportedLinkCount(McsaFileError):
    pass


class ModelError(ScFileException):
    pass
