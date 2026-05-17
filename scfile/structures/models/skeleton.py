from dataclasses import dataclass, field
from typing import List, Self

import numpy as np

from scfile.consts import ModelDefaults

from .enums import SkeletonHierarchy, SkeletonSpace
from .matrices import create_transform_matrix, euler_to_quat
from .types import BindPose, EulerAngles, InverseBindMatrices, Quaternion, Vector3D


@dataclass
class SkeletonBone:
    """Single skeleton bone with transform data."""

    id: int = 0
    name: str = "bone"
    parent_id: int = ModelDefaults.ROOT_BONE_ID

    position: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    rotation: EulerAngles = field(default_factory=lambda: np.zeros(3, dtype=np.float32))

    children: List[Self] = field(default_factory=list, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent_id == ModelDefaults.ROOT_BONE_ID

    @property
    def quaternion(self) -> Quaternion:
        return euler_to_quat(self.rotation)

    @property
    def slug(self) -> str:
        return "".join(ch for ch in self.name.lower() if ch.isalnum())


@dataclass
class ModelSkeleton:
    """Skeleton bones container."""

    bones: List[SkeletonBone] = field(default_factory=list)
    space: SkeletonSpace = SkeletonSpace.GLOBAL
    hierarchy: SkeletonHierarchy = SkeletonHierarchy.FLAT

    @property
    def roots(self) -> List[SkeletonBone]:
        return list(filter(lambda bone: bone.is_root, self.bones))

    def calculate_global_transforms(self) -> BindPose:
        transforms: BindPose = []

        for bone in self.bones:
            local_matrix = create_transform_matrix(bone.position, bone.rotation)
            global_matrix = local_matrix if bone.is_root else transforms[bone.parent_id] @ local_matrix
            transforms.append(global_matrix)

        return transforms

    def inverse_bind_matrices(self, transpose: bool) -> InverseBindMatrices:
        global_transforms = self.calculate_global_transforms()

        inverse_matrices = [np.linalg.inv(matrix) for matrix in global_transforms]

        if transpose:
            inverse_matrices = [matrix.T for matrix in inverse_matrices]

        return np.array(inverse_matrices, dtype=np.float32)
