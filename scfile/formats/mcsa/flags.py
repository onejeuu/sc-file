from enum import IntEnum, auto


class Flag(IntEnum):
    SKELETON = 0
    TEXTURE = auto()
    NORMALS = auto()
    UNKNOWN_A = auto()
    UNKNOWN_B = auto()
    COLORS = auto()


def to_named_dict(flags: dict[int, bool]):
    return {Flag(key).name: value for key, value in flags.items()}
