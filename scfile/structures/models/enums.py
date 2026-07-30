"""
Enums for model data structures.
"""

from enum import IntEnum, StrEnum, auto


class Feature(StrEnum):
    """Optional model feature."""

    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()
    SKELETON = auto()
    BLEND_SHAPES = auto()
    ANIMATION = auto()
    BONE_ANIMATION = auto()
    MORPH_ANIMATION = auto()

    @property
    def members(self) -> tuple["Feature", ...]:
        """Concrete features represented by this feature."""

        if self is Feature.ANIMATION:
            return (
                Feature.BONE_ANIMATION,
                Feature.MORPH_ANIMATION,
            )

        return (self,)

    @property
    def requires(self) -> tuple["Feature", ...]:
        """Features required to serialize this feature."""

        if self is Feature.BONE_ANIMATION:
            return (Feature.SKELETON,)

        return ()

    @property
    def parent(self) -> "Feature":
        """Parent feature used for shared behavior."""

        if self in Feature.ANIMATION.members:
            return Feature.ANIMATION

        return self


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
