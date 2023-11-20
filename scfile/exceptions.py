from pathlib import Path
from typing import TypeAlias
from scfile.utils.mcsa_flags import McsaFlags

StringOrPath: TypeAlias = str | Path


# * base exception
class ScFileException(Exception): ...


# * basic
class ScFileBasicError(ScFileException):
    def __init__(self, path: StringOrPath):
        self.path = Path(path)

    @property
    def posix_path(self) -> str:
        return self.path.as_posix()

    def __str__(self):
        return f"File '{self.posix_path}'"

class SourceFileNotFound(ScFileBasicError):
    def __str__(self):
        return f"{super().__str__()} not found (not exists)."

class UnsupportedSuffix(ScFileBasicError):
    def __str__(self):
        return f"{super().__str__()} with suffix '{self.path.suffix}' is unsupported."

class FileIsEmpty(ScFileBasicError):
    def __str__(self):
        return f"{super().__str__()} is empty."

class InvalidSignature(ScFileBasicError):
    def __init__(self, path: StringOrPath, signature: int, valid_signature: int):
        self.path = Path(path)
        self.signature = signature
        self.valid_signature = valid_signature

    def __str__(self):
        return (
            f"{super().__str__()} has invalid signature - "
            f"{hex(self.signature)} != {hex(self.valid_signature)}. "
            "(File suffix does not match file type)."
        )


# * binary reader
class ReaderError(ScFileException): ...
class ReadingMcsaStringError(ReaderError): ...
class ReadingOlStringError(ReaderError): ...


# * converting file
class ConvertingFileError(ScFileException):
    def __init__(self, path: StringOrPath):
        self.path = Path(path)

    @property
    def posix_path(self) -> str:
        return self.path.as_posix()


# * .ol files
class OlFileError(ConvertingFileError):
    def __str__(self):
        return f"Texture '{self.posix_path}'"

class OlUnsupportedFormat(OlFileError):
    def __init__(self, path: StringOrPath, fourcc: str):
        self.path = Path(path)
        self.fourcc = fourcc

    def __str__(self):
        return f"{super().__str__()} has unsupported format '{self.fourcc}'"

class OlDXNError(OlFileError): ...
class OlDXNSize(OlDXNError): ...
class OlDXNNotSquare(OlDXNError): ...


# * .mcsa files
class McsaFileError(ConvertingFileError):
    def __str__(self):
        return f"Model '{self.posix_path}'"

class McsaUnsupportedVersion(McsaFileError):
    def __init__(self, path: StringOrPath, version: float):
        self.path = Path(path)
        self.version = version

    def __str__(self):
        return f"{super().__str__()} has unsupported version: {self.version}"

class McsaUnsupportedFlags(McsaFileError):
    def __init__(self, path: StringOrPath, flags: McsaFlags):
        self.path = Path(path)
        self.flags = flags

    def __str__(self):
        return f"{super().__str__()} has unsupported flags: {self.flags}"

class McsaUnsupportedLinkCount(McsaFileError):
    def __init__(self, path: StringOrPath, link_count: int):
        self.path = Path(path)
        self.link_count = link_count

    def __str__(self):
        return f"{super().__str__()} has unsupported bones link count: {self.link_count}"
