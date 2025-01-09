from enum import IntEnum


class ComponentType(IntEnum):
    UBYTE = 5121
    FLOAT = 5126
    UINT16 = 5123
    UINT32 = 5125


class BufferTarget(IntEnum):
    ARRAY_BUFFER = 34962
    ELEMENT_ARRAY_BUFFER = 34963


class PrimitiveMode(IntEnum):
    TRIANGLES = 4
