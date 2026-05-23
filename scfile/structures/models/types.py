"""
Type aliases for model data structures.
"""

from typing import Annotated, NewType, TypeAlias

import numpy as np
from numpy.typing import NDArray

from .enums import Flag


ModelFlags: TypeAlias = dict[Flag, bool]
"""Per-feature presence flags."""

Vector2D: TypeAlias = Annotated[NDArray[np.float32], (..., 2)]
"""2D float32 vector."""
Vector3D: TypeAlias = Annotated[NDArray[np.float32], (..., 3)]
"""3D float32 vector."""
Vector4D: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
"""4D float32 vector."""

LinksIds: TypeAlias = Annotated[NDArray[np.uint8], (..., 4)]
"""Bone indices per vertex."""
LinksWeights: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
"""Bone weights per vertex."""
Links: TypeAlias = tuple[LinksIds, LinksWeights]
"""Bone indices and weights pair."""

LocalBoneId = NewType("LocalBoneId", int)
"""Bone index within mesh."""
SkeletonBoneId = NewType("SkeletonBoneId", int)
"""Bone index within skeleton."""
BonesMapping: TypeAlias = dict[LocalBoneId, SkeletonBoneId]
"""Mapping from mesh local to skeleton bone indices."""

Polygons: TypeAlias = Annotated[NDArray[np.uint32], (..., 3)]
"""Triangle indices."""

Colors: TypeAlias = Annotated[NDArray[np.uint8], (..., 4)]
"""RGBA vertex colors."""

EulerAngles: TypeAlias = Annotated[NDArray[np.float32], (..., 3)]
"""Euler angles in degrees (XYZ intrinsic)."""
Quaternion: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
"""Quaternion rotation (XYZW)."""

RotationMatrix: TypeAlias = Annotated[NDArray[np.float32], (3, 3)]
"""3x3 rotation matrix."""
TransformMatrix: TypeAlias = Annotated[NDArray[np.float32], (4, 4)]
"""4×4 transformation matrix."""

BindPose: TypeAlias = list[TransformMatrix]
"""Global transform per bone."""
InverseBindMatrices: TypeAlias = Annotated[NDArray[np.float32], (..., 4, 4)]
"""Inverse bind matrices per bone."""

AnimationTranslations: TypeAlias = Annotated[NDArray[np.float32], (..., 3)]
"""Animation translations per frame."""
AnimationRotations: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
"""Animation rotations per frame."""
AnimationTimes: TypeAlias = Annotated[NDArray[np.float32], (...)]
"""Animation times per frame."""
