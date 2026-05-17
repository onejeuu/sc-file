from enum import StrEnum, auto


class FlagKey(StrEnum):
    SKELETON = auto()
    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()


Flag = FlagKey


class UVOrigin(StrEnum):
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()


class UVSign(StrEnum):
    POSITIVE = auto()
    NEGATIVE = auto()


class LinkSpace(StrEnum):
    GLOBAL = auto()
    LOCAL = auto()


class SkeletonSpace(StrEnum):
    GLOBAL = auto()
    LOCAL = auto()


class SkeletonHierarchy(StrEnum):
    FLAT = auto()
    BUILT = auto()


class AnimationTranslation(StrEnum):
    DELTA = auto()
    ABSOLUTE = auto()


class AnimationRotation(StrEnum):
    QUATERNION = auto()
    EULER = auto()
