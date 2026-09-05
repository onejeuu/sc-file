"""Scene structures."""

from dataclasses import dataclass, field
from typing import assert_never

import numpy as np

from .enums import AnimationRotation, AnimationTranslation, Feature, SkeletonSpace
from .matrices import euler_to_quat
from .mesh import ModelMesh
from .types import (
    AnimationRotations,
    AnimationTimes,
    AnimationTranslations,
    EulerAngles,
    InverseBindMatrices,
    MorphWeights,
    Quaternion,
    Vector3D,
)


ROOT_BONE_ID = -1
"""Default parent ID for root bones."""


@dataclass
class SkeletonBone:
    """Bone with transform data."""

    id: int = 0
    name: str = "bone"
    parent_id: int = ROOT_BONE_ID

    position: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    rotation: EulerAngles = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    tail: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))

    @property
    def is_root(self) -> bool:
        return self.parent_id == ROOT_BONE_ID

    @property
    def quaternion(self) -> Quaternion:
        return euler_to_quat(self.rotation)

    @property
    def slug(self) -> str:
        return "".join(ch for ch in self.name.lower() if ch.isalnum())


@dataclass
class ModelSkeleton:
    """Skeleton bones container."""

    bones: list[SkeletonBone] = field(default_factory=list)
    space: SkeletonSpace = SkeletonSpace.GLOBAL

    @property
    def roots(self) -> list[SkeletonBone]:
        return [bone for bone in self.bones if bone.is_root]


@dataclass
class AnimationClip:
    """Keyframed bone and morph animation clip."""

    name: str = "clip"
    frames: int = 0
    rate: float = 0.33
    translations: AnimationTranslations = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))
    rotations: AnimationRotations = field(default_factory=lambda: np.zeros((0, 4), dtype=np.float32))
    morph_weights: MorphWeights = field(default_factory=lambda: np.zeros((0, 0), dtype=np.float32))

    @property
    def times(self) -> AnimationTimes:
        return np.arange(self.frames, dtype=np.float32) * self.rate


@dataclass
class ModelAnimation:
    """Animation clips container."""

    clips: list[AnimationClip] = field(default_factory=list)
    morph_channels: list[str] = field(default_factory=list)
    translation: AnimationTranslation = AnimationTranslation.DELTA
    rotation: AnimationRotation = AnimationRotation.QUATERNION


@dataclass
class SceneScales:
    """Scale multipliers for scene data."""

    position: float = 1.0
    uv: float = 1.0
    uv2: float = 1.0


@dataclass
class ModelSkin:
    """Bind matrices used by meshes in an assembled scene."""

    bind_matrices: InverseBindMatrices


@dataclass
class ModelScene:
    """Container for meshes, skeleton, and animation."""

    scale: SceneScales = field(default_factory=SceneScales)

    meshes: list[ModelMesh] = field(default_factory=list)
    skins: list[ModelSkin] = field(default_factory=list)
    skeleton: ModelSkeleton = field(default_factory=ModelSkeleton)
    animation: ModelAnimation = field(default_factory=ModelAnimation)

    def has(
        self,
        feature: Feature,
    ) -> bool:
        """Return whether scene contains a feature."""

        match feature:
            case Feature.UV:
                return any(mesh.uv1.size for mesh in self.meshes)

            case Feature.UV2:
                return any(mesh.uv2.size for mesh in self.meshes)

            case Feature.NORMALS:
                return any(mesh.normals.size for mesh in self.meshes)

            case Feature.TANGENTS:
                return any(mesh.tangents.size for mesh in self.meshes)

            case Feature.COLORS:
                return any(mesh.colors.size for mesh in self.meshes)

            case Feature.SKELETON:
                return bool(self.skeleton.bones)

            case Feature.BLEND_SHAPES:
                return any(mesh.blend_shapes for mesh in self.meshes)

            case Feature.ANIMATION:
                return any(self.has(member) for member in feature.members)

            case Feature.BONE_ANIMATION:
                return any(clip.translations.size and clip.rotations.size for clip in self.animation.clips)

            case Feature.MORPH_ANIMATION:
                return any(clip.morph_weights.size for clip in self.animation.clips)

            case _:
                assert_never(feature)

    @property
    def total_vertices(self) -> int:
        return sum(len(mesh.vertices) for mesh in self.meshes)

    @property
    def total_polygons(self) -> int:
        return sum(len(mesh.polygons) for mesh in self.meshes)
