from enum import StrEnum, auto


class FileFormat(StrEnum):
    """File suffix (without dot)."""

    DAE = auto()
    DDS = auto()
    GLB = auto()
    JSON = auto()
    MCAL = auto()
    MCSA = auto()
    MCSB = auto()
    MCVD = auto()
    MIC = auto()
    MS3D = auto()
    NBT = auto()
    OBJ = auto()
    OL = auto()
    PNG = auto()
    TEXARR = auto()
    ZIP = auto()
    ITEMNAMES = "dat"  # NBT

    @property
    def suffix(self):
        return f".{self.value.lower()}"


class FileType(StrEnum):
    """File content type."""

    NONE = auto()
    MODEL = auto()
    TEXTURE = auto()
    IMAGE = auto()
    TEXARR = auto()
    NBT = auto()


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


class StructFormat(StrEnum):
    """Native C-type struct format codes."""

    BOOL = "?"
    """boolean: `BOOL` `1 byte` [False, True]"""

    I8 = "b"
    """signed char: `BYTE` `1 byte` [-128, 127]"""
    I16 = "h"
    """signed short: `WORD` `2 bytes` [-32768, 32767]"""
    I32 = "i"
    """signed int: `DWORD` `4 bytes` [-2147483648, 2147483647]"""
    I64 = "q"
    """signed long long: `QWORD` `8 bytes` [-9223372036854775808, 9223372036854775807]"""

    U8 = "B"
    """unsigned char: `BYTE` `1 byte` [0, 255]"""
    U16 = "H"
    """unsigned short: `WORD` `2 bytes` [0, 65535]"""
    U32 = "I"
    """unsigned int: `DWORD` `4 bytes` [0, 4294967295]"""
    U64 = "Q"
    """unsigned long long: `QWORD` `8 bytes` [0, 18446744073709551615]"""

    F16 = "e"
    """float: `half-precision` `2 bytes`"""
    F32 = "f"
    """double: `single-precision` `4 bytes`"""
    F64 = "d"
    """double: `double-precision` `8 bytes`"""


F = StructFormat
"""StructFormat Alias."""


class ConsoleLabel(StrEnum):
    """Colored labels for console output."""

    INFO = "[b blue]INFO:[/]"
    HINT = "[b cyan]HINT:[/]"
    WARN = "[b yellow]WARN:[/]"
    ERROR = "[b red]ERROR:[/]"
    INVALID = "[b red]INVALID INPUT:[/]"
    EXCEPTION = "[b red]UNEXPECTED ERROR:[/]"


L = ConsoleLabel
"""ConsoleLabel Alias."""
