"""Data structures for skeletons."""

from dataclasses import dataclass, field

import numpy as np

from .enums import SkeletonSpace
from .matrices import euler_to_quat
from .types import EulerAngles, Quaternion, Vector3D


ROOT_BONE_ID = -1
"""Parent ID used by root bones."""


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
