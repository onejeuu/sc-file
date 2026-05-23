"""
Enums for model data structures.
"""

from enum import StrEnum, auto


class Flag(StrEnum):
    """Model feature flag."""

    SKELETON = auto()
    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()


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
