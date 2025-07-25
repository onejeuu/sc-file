"""
Dataclasses for 3D model armature.
"""

from dataclasses import dataclass, field
from typing import List, Self

import numpy as np

from scfile.consts import McsaModel

from .vectors import Vector3D, Vector4D


@dataclass
class SkeletonBone:
    """Single skeleton bone with transform data."""

    id: int = 0
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID

    position: Vector3D = field(default_factory=lambda: np.empty(3, dtype=np.float32))
    rotation: Vector3D = field(default_factory=lambda: np.empty(3, dtype=np.float32))

    children: List[Self] = field(default_factory=list, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent_id == McsaModel.ROOT_BONE_ID

    @property
    def quaternion(self) -> Vector4D:
        return euler_to_quat(self.rotation)


@dataclass
class ModelSkeleton:
    """Skeleton bones container."""

    bones: List[SkeletonBone] = field(default_factory=list)

    @property
    def roots(self) -> List[SkeletonBone]:
        return list(filter(lambda bone: bone.is_root, self.bones))

    def convert_to_local(self) -> None:
        for bone in self.bones:
            parent_id = bone.parent_id

            # Convert global position to parent-relative space
            while parent_id > McsaModel.ROOT_BONE_ID:
                parent = self.bones[parent_id]
                bone.position -= parent.position  # Make position relative to parent
                parent_id = parent.parent_id  # Move up hierarchy

    def build_hierarchy(self) -> None:
        # Rebuild hierarchy
        for bone in self.bones:
            if not bone.is_root:
                parent = self.bones[bone.parent_id]
                parent.children.append(bone)

    def calculate_global_transforms(self) -> list[np.ndarray]:
        transforms: list[np.ndarray] = []

        for bone in self.bones:
            local_matrix = create_transform_matrix(bone.position, bone.rotation)
            global_matrix = local_matrix if bone.is_root else transforms[bone.parent_id] @ local_matrix
            transforms.append(global_matrix)

        return transforms

    def inverse_bind_matrices(self, transpose: bool) -> np.ndarray:
        global_transforms = self.calculate_global_transforms()

        inverse_matrices = [np.linalg.inv(matrix) for matrix in global_transforms]

        if transpose:
            inverse_matrices = [matrix.T for matrix in inverse_matrices]

        return np.array(inverse_matrices, dtype=np.float32)


def create_rotation_matrix(rotation: Vector3D) -> np.ndarray:
    angles = np.radians(rotation)
    cx, cy, cz = np.cos(angles)
    sx, sy, sz = np.sin(angles)

    return np.array(
        [
            [cy * cz, -cy * sz, sy],
            [cx * sz + cz * sx * sy, cx * cz - sx * sy * sz, -cy * sx],
            [sx * sz - cx * cz * sy, cz * sx + cx * sy * sz, cx * cy],
        ],
        dtype=np.float32,
    )


def create_transform_matrix(position: Vector3D, rotation: Vector3D) -> np.ndarray:
    matrix = np.eye(4, dtype=np.float32)
    matrix[:3, :3] = create_rotation_matrix(rotation)
    matrix[:3, 3] = position
    return matrix


def euler_to_quat(rotation: Vector3D, degrees: bool = True) -> Vector4D:
    x, y, z = np.radians(rotation) if degrees else rotation
    hx, hy, hz = x * 0.5, y * 0.5, z * 0.5

    cx, cy, cz = np.cos([hx, hy, hz])
    sx, sy, sz = np.sin([hx, hy, hz])

    return np.array(
        [
            sx * cy * cz - cx * sy * sz,
            cx * sy * cz + sx * cy * sz,
            cx * cy * sz - sx * sy * cz,
            cx * cy * cz + sx * sy * sz,
        ],
        dtype=np.float32,
    )
