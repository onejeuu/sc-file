"""
Data structures for 3D model content.
"""

from .animation import AnimationClip, ModelAnimation
from .enums import (
    AnimationRotation,
    AnimationTranslation,
    Flag,
    LinkSpace,
    SkeletonHierarchy,
    SkeletonSpace,
    UVOrigin,
    UVSign,
)
from .matrices import create_rotation_matrix, create_transform_matrix, euler_to_quat
from .mesh import MeshBounds, ModelMesh
from .scene import ModelScene, SceneScales
from .skeleton import ModelSkeleton, SkeletonBone
from .types import (
    AnimationRotations,
    AnimationTimes,
    AnimationTranslations,
    BindPose,
    BonesMapping,
    Colors,
    EulerAngles,
    InverseBindMatrices,
    Links,
    LinksIds,
    LinksWeights,
    LocalBoneId,
    ModelFlags,
    Polygons,
    Quaternion,
    RotationMatrix,
    SkeletonBoneId,
    TransformMatrix,
    Vector2D,
    Vector3D,
    Vector4D,
)


__all__ = (
    "AnimationClip",
    "MeshBounds",
    "ModelAnimation",
    "ModelMesh",
    "ModelScene",
    "SceneScales",
    "SkeletonBone",
    "ModelSkeleton",
    "Flag",
    "AnimationRotations",
    "AnimationTimes",
    "AnimationTranslations",
    "BindPose",
    "BonesMapping",
    "Colors",
    "EulerAngles",
    "InverseBindMatrices",
    "Links",
    "LinksIds",
    "LinksWeights",
    "LocalBoneId",
    "ModelFlags",
    "Polygons",
    "Quaternion",
    "RotationMatrix",
    "SkeletonBoneId",
    "TransformMatrix",
    "Vector2D",
    "Vector3D",
    "Vector4D",
    "AnimationRotation",
    "AnimationTranslation",
    "LinkSpace",
    "SkeletonHierarchy",
    "SkeletonSpace",
    "UVOrigin",
    "UVSign",
    "create_rotation_matrix",
    "create_transform_matrix",
    "euler_to_quat",
)
