from enum import IntEnum


class PropertyType(IntEnum):
    INT16 = ord("Y")
    BOOL = ord("C")
    INT32 = ord("I")
    FLOAT = ord("F")
    DOUBLE = ord("D")
    INT64 = ord("L")
    STRING = ord("S")
    RAW = ord("R")
    ARRAY_DOUBLE = ord("d")
    ARRAY_INT32 = ord("i")
    ARRAY_INT64 = ord("l")
    ARRAY_FLOAT = ord("f")
    ARRAY_BOOL = ord("b")
