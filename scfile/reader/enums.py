from enum import Enum, StrEnum
from typing import NamedTuple


class ByteOrder(Enum):
    NATIVE = "@"
    STANDART = "="
    LITTLE = "<"
    BIG = ">"
    NETWORK = "!"


class Format(StrEnum):
    I8 = "b"
    I16 = "h"
    I32 = "i"
    I64 = "q"

    U8 = "B"
    U16 = "H"
    U32 = "I"
    U64 = "Q"

    F16 = "e"
    F32 = "f"
    F64 = "d"


class OlString(NamedTuple):
    SIZE = 16
    XOR = 0x67
    NULL = 0x47
