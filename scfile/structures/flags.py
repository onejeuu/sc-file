"""
Enum for 3D scene flags.
"""

from enum import StrEnum, auto


class Flag(StrEnum):
    SKELETON = auto()
    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()



def to_named_dict(flags: dict[int, bool]):
    return {Flag(key).name: value for key, value in flags.items()}
