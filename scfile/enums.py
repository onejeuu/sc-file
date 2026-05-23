from enum import StrEnum, auto


class FileFormat(StrEnum):
    """File extension without dot."""

    NONE = ""
    DAE = auto()
    DDS = auto()
    EFKMODEL = auto()
    FBX = auto()
    GLB = auto()
    JSON = auto()
    MCA = auto()
    MCAL = auto()
    MCSA = auto()
    MCSB = auto()
    MCVD = auto()
    MDAT = auto()
    MIC = auto()
    MS3D = auto()
    NBT = auto()
    OBJ = auto()
    OL = auto()
    PNG = auto()
    TEXARR = auto()
    ZIP = auto()

    @property
    def suffix(self):
        return f".{self.value.lower()}" if self.value else ""


class FileType(StrEnum):
    """File content kind."""

    NONE = auto()
    MODEL = auto()
    TEXTURE = auto()
    IMAGE = auto()
    TEXARR = auto()
    NBT = auto()
    REGION = auto()


class ByteOrder(StrEnum):
    """File data byte order."""

    NATIVE = "@"
    STANDARD = "="
    LITTLE = "<"
    BIG = ">"
    NETWORK = "!"


class UnicodeErrors(StrEnum):
    """Unicode error handling policy."""

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
    """C-type struct format codes."""

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
    """Colored console output labels."""

    INFO = "[b blue]INFO:[/]"
    HINT = "[b cyan]HINT:[/]"
    DONE = "[b green]DONE:[/]"
    WARN = "[b yellow]WARN:[/]"
    ERROR = "[b red]ERROR:[/]"
    INVALID = "[b red]INVALID INPUT:[/]"
    EXCEPTION = "[b red]UNEXPECTED ERROR:[/]"


L = ConsoleLabel
"""ConsoleLabel Alias."""


class CliCommand(StrEnum):
    """CLI command names."""

    CONVERT = auto()
    MAPCACHE = auto()


class UpdateStatus(StrEnum):
    """Update check result status."""

    ERROR = auto()
    UPTODATE = auto()
    AVAILABLE = auto()
