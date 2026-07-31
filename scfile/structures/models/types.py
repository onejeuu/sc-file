"""
Type aliases for model data structures.
"""

from typing import Annotated, NewType

import numpy as np
from numpy.typing import NDArray

from .enums import Feature


type Features = tuple[Feature, ...]
"""Model feature collection."""

type FeatureFlags = dict[Feature, bool]
"""Feature flags declared by source model."""


LocalBoneId = NewType("LocalBoneId", int)
"""Bone index within mesh."""
SkeletonBoneId = NewType("SkeletonBoneId", int)
"""Bone index within skeleton."""

type BonesMapping = dict[LocalBoneId, SkeletonBoneId]
"""Mapping from mesh local to skeleton bone indices."""

type Vector2D = Annotated[NDArray[np.float32], (..., 2)]
"""2D float32 vector."""
type Vector3D = Annotated[NDArray[np.float32], (..., 3)]
"""3D float32 vector."""
type Vector4D = Annotated[NDArray[np.float32], (..., 4)]
"""4D float32 vector."""

type LinksIds = Annotated[NDArray[np.uint8], (..., 4)]
"""Bone indices per vertex."""
type LinksWeights = Annotated[NDArray[np.float32], (..., 4)]
"""Bone weights per vertex."""
type Links = tuple[LinksIds, LinksWeights]
"""Bone indices and weights pair."""

type Polygons = Annotated[NDArray[np.uint32], (..., 3)]
"""Triangle indices."""

type BlendVertexMap = Annotated[NDArray[np.uint16], (...,)]
"""Blend shape base vertex index per mesh vertex."""

type Colors = Annotated[NDArray[np.uint8], (..., 4)]
"""RGBA vertex colors."""

type EulerAngles = Annotated[NDArray[np.float32], (..., 3)]
"""Euler angles in degrees (XYZ intrinsic)."""
type Quaternion = Annotated[NDArray[np.float32], (..., 4)]
"""Quaternion rotation (XYZW)."""

type RotationMatrix = Annotated[NDArray[np.float32], (3, 3)]
"""3x3 rotation matrix."""
type TransformMatrix = Annotated[NDArray[np.float32], (4, 4)]
"""4×4 transformation matrix."""

type BindPose = list[TransformMatrix]
"""Global transform per bone."""
type InverseBindMatrices = Annotated[NDArray[np.float32], (..., 4, 4)]
"""Inverse bind matrices per bone."""

type AnimationTranslations = Annotated[NDArray[np.float32], (..., 3)]
"""Animation translations per frame."""
type AnimationRotations = Annotated[NDArray[np.float32], (..., 4)]
"""Animation rotations per frame."""
type AnimationTimes = Annotated[NDArray[np.float32], (...)]
"""Animation times per frame."""
type MorphWeights = NDArray[np.float32]
"""Morph channel weights per frame."""
