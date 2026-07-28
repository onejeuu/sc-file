"""
Enums for model data structures.
"""

from enum import IntEnum, StrEnum, auto


class Flag(StrEnum):
    """Model feature flag."""

    SKELETON = auto()
    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()


class ModelUnits(IntEnum):
    """Model structure element counts."""

    POSITIONS = 4
    TEXTURES = 2
    NORMALS = 4
    TANGENTS = 4
    TRIANGLES = 3
    QUADS = 4
    LINKS = 4
    BONES = 6
    FRAMES = 7


class UVOrigin(StrEnum):
    """UV coordinate origin."""

    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()


class UVSign(StrEnum):
    """UV coordinate sign."""

    POSITIVE = auto()
    NEGATIVE = auto()


class LinkSpace(StrEnum):
    """Vertex link coordinate space."""

    GLOBAL = auto()
    LOCAL = auto()


class SkeletonSpace(StrEnum):
    """Skeleton bones coordinate space."""

    GLOBAL = auto()
    LOCAL = auto()


class SkeletonHierarchy(StrEnum):
    """Skeleton bones hierarchy state."""

    FLAT = auto()
    BUILT = auto()


class AnimationTranslation(StrEnum):
    """Animation translation mode."""

    DELTA = auto()
    ABSOLUTE = auto()


class AnimationRotation(StrEnum):
    """Animation rotation format."""

    QUATERNION = auto()
    EULER = auto()
