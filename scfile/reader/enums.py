from enum import StrEnum


class ByteOrder(StrEnum):
    NATIVE = "@"
    STANDARD = "="
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
