"""
Dataclasses for 3D model armature.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Self

import numpy as np

from scfile.consts import McsaModel

from .vectors import Vector3D, Vector4D


@dataclass
class SkeletonBone:
    id: int = 0
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID
    position: Vector3D = field(default_factory=lambda: np.empty(3, dtype=np.float32))
    rotation: Vector3D = field(default_factory=lambda: np.empty(3, dtype=np.float32))
    children: List[Self] = field(default_factory=list, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent_id == McsaModel.ROOT_BONE_ID


@dataclass
class ModelSkeleton:
    bones: List[SkeletonBone] = field(default_factory=list)
    roots: List[SkeletonBone] = field(default_factory=list)

    def convert_to_local(self) -> None:
        """Update bones positions by their parent bone."""
        parent_id = 0
        bones = self.bones

        for bone in bones:
            parent_id = bone.parent_id

            # Update position relative to parent
            while parent_id > McsaModel.ROOT_BONE_ID:
                parent = bones[parent_id]
                bone.position -= parent.position
                parent_id = parent.parent_id

    def build_hierarchy(self) -> list[SkeletonBone]:
        """Fills bones children list."""
        # Create a dictionary to map bone id to bones
        bone_dict: Dict[int, SkeletonBone] = {bone.id: bone for bone in self.bones}

        # Find the root bones (those without a parent)
        roots: List[SkeletonBone] = []

        # Assign children to their respective parents
        for bone in self.bones:
            if bone.is_root:
                roots.append(bone)
                continue

            # Add bone to parents children
            if parent := bone_dict.get(bone.parent_id):
                parent.children.append(bone)

        self.roots = roots
        return roots

    def calculate_global_transforms(self) -> list[np.ndarray]:
        global_transforms: list[np.ndarray] = []

        for bone in self.bones:
            local_matrix = create_transform_matrix(bone.position, bone.rotation)
            global_transform = local_matrix if bone.is_root else global_transforms[bone.parent_id] @ local_matrix
            global_transforms.append(global_transform)

        return global_transforms

    def inverse_bind_matrices(self, transpose: bool) -> np.ndarray:
        global_transforms = self.calculate_global_transforms()
        inverse_matrices = [np.linalg.inv(transform.T if transpose else transform) for transform in global_transforms]

        return np.round(inverse_matrices, decimals=McsaModel.DECIMALS)


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


def euler_to_quat(rotation: Vector3D, degrees=True) -> Vector4D:
    x, y, z = rotation

    if degrees:
        x, y, z = np.radians(x), np.radians(y), np.radians(z)

    cy = np.cos(z * 0.5)
    sy = np.sin(z * 0.5)
    cp = np.cos(y * 0.5)
    sp = np.sin(y * 0.5)
    cr = np.cos(x * 0.5)
    sr = np.sin(x * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return np.array([qx, qy, qz, qw])
