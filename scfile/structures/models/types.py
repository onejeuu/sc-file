from typing import Annotated, NewType, TypeAlias

import numpy as np
from numpy.typing import NDArray

from .enums import Flag


ModelFlags: TypeAlias = dict[Flag, bool]

Vector2D: TypeAlias = Annotated[NDArray[np.float32], (..., 2)]
Vector3D: TypeAlias = Annotated[NDArray[np.float32], (..., 3)]
Vector4D: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
LinksIds: TypeAlias = Annotated[NDArray[np.uint8], (..., 4)]
LinksWeights: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
Links: TypeAlias = tuple[LinksIds, LinksWeights]
Polygons: TypeAlias = Annotated[NDArray[np.uint32], (..., 3)]

EulerAngles: TypeAlias = Annotated[NDArray[np.float32], (..., 3)]
Quaternion: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
RotationMatrix: TypeAlias = Annotated[NDArray[np.float32], (3, 3)]
TransformMatrix: TypeAlias = Annotated[NDArray[np.float32], (4, 4)]
BindPose: TypeAlias = list[TransformMatrix]
InverseBindMatrices: TypeAlias = Annotated[NDArray[np.float32], (..., 4, 4)]
AnimationTransforms: TypeAlias = Annotated[NDArray[np.float32], (..., 7)]
AnimationTimes: TypeAlias = Annotated[NDArray[np.float32], (...)]

LocalBoneId = NewType("LocalBoneId", int)
SkeletonBoneId = NewType("SkeletonBoneId", int)
BonesMapping: TypeAlias = dict[LocalBoneId, SkeletonBoneId]
