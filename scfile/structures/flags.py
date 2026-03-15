"""
Enum for 3D scene flags.
"""

from enum import StrEnum, auto


class FlagKey(StrEnum):
    SKELETON = auto()
    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()


Flag = FlagKey
