from enum import StrEnum, auto


class FileSuffix(StrEnum):
    DDS = auto()
    MCSA = auto()
    MCVD = auto()
    MIC = auto()
    OBJ = auto()
    TXT = auto()
    OL = auto()
    PNG = auto()


class FileMode(StrEnum):
    RB = READ = auto()
    WB = WRITE = auto()
    AB = APPEND = auto()
    PLUS = "+"


class ByteOrder(StrEnum):
    NATIVE = "@"
    STANDARD = "="
    LITTLE = "<"
    BIG = ">"
    NETWORK = "!"


class StructFormat(StrEnum):
    BOOL = "?"
    """boolean: `1 byte` [False, True]"""

    CHAR = "c"
    """character: `1 byte` [0, 255]"""

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
