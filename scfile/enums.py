from enum import StrEnum, auto


class FileFormat(StrEnum):
    """File suffix (without dot)."""

    DAE = auto()
    DDS = auto()
    FBX = auto()
    GLB = auto()
    MCAL = auto()
    MCSA = auto()
    MCSB = auto()
    MCVD = auto()
    MIC = auto()
    MS3D = auto()
    OBJ = auto()
    OL = auto()
    PNG = auto()
    TXT = MS3D_ASCII = auto()


class FileType(StrEnum):
    """File content type."""

    MODEL = auto()
    TEXTURE = auto()
    IMAGE = auto()


class FileMode(StrEnum):
    """File open mode."""

    RB = READ = auto()
    WB = WRITE = auto()
    AB = APPEND = auto()
    PLUS = "+"


class ByteOrder(StrEnum):
    """File content bytes order."""

    NATIVE = "@"
    STANDARD = "="
    LITTLE = "<"
    BIG = ">"
    NETWORK = "!"


class StructFormat(StrEnum):
    """Native C-type struct format codes."""

    BOOL = "?"
    """boolean: `1 byte` [False, True]"""

    I8 = "b"
    """signed char: `BYTE` `1 byte` [-128, 127]"""
    I16 = "h"
    """signed short: `WORD` `2 bytes` [-32768, 32767]"""
    I32 = "i"
    """signed int: `DWORD` `4 bytes` [-2147483648, 2147483647]"""

    U8 = "B"
    """unsigned char: `BYTE` `1 byte` [0, 255]"""
    U16 = "H"
    """unsigned short: `WORD` `2 bytes` [0, 65535]"""
    U32 = "I"
    """unsigned int: `DWORD` `4 bytes` [0, 4294967295]"""

    F16 = "e"
    """float: `half-precision` `2 bytes`"""
    F32 = "f"
    """double: `single-precision` `4 bytes`"""


class UnicodeErrors(StrEnum):
    """Unicode errors handling policy."""

    STRICT = auto()
    """Raise UnicodeDecodeError on invalid bytes"""
    IGNORE = auto()
    """Skip invalid bytes silently"""
    REPLACE = auto()
    """Replace invalid bytes with a replacement marker (�)"""

    BACKSLASHREPLACE = BACKSLASH = auto()
    """Replace with backslash-escaped sequences (\\xHH)"""
    NAMEREPLACE = NAME = auto()
    """Replace with \\N{...} escape sequences"""
    XMLCHARREFREPLACE = XML = auto()
    """Replace with XML/HTML numeric entities (&#...;)"""

    SURROGATEESCAPE = SURROGATE = auto()
    """Preserve invalid bytes as surrogate codes"""
