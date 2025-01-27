from dataclasses import dataclass, field
from typing import Dict, List, Self

import numpy as np

from scfile.consts import McsaModel

from .vectors import Vector3


ROOT = McsaModel.ROOT_BONE_ID


@dataclass
class SkeletonBone:
    id: int = 0
    name: str = "bone"
    parent_id: int = ROOT
    position: Vector3 = field(default_factory=Vector3)
    rotation: Vector3 = field(default_factory=Vector3)
    children: List[Self] = field(default_factory=list, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent_id == ROOT


@dataclass
class ModelSkeleton:
    bones: List[SkeletonBone] = field(default_factory=list)
    roots: List[SkeletonBone] = field(default_factory=list)

    def convert_to_local(self):
        """Update bones positions by their parent bone."""
        parent_id = 0
        bones = self.bones

        for bone in bones:
            parent_id = bone.parent_id

            # Update position relative to parent
            while parent_id > ROOT:
                parent = bones[parent_id]
                bone.position -= parent.position
                parent_id = parent.parent_id

    def build_hierarchy(self):
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

    def calculate_global_transforms(self) -> List[np.ndarray]:
        global_transforms = []

        for bone in self.bones:
            local_transform = create_transform_matrix(bone)

            if bone.is_root:
                global_transform = local_transform
            else:
                parent_transform = global_transforms[bone.parent_id]
                global_transform = parent_transform @ local_transform

            global_transforms.append(global_transform)

        return global_transforms

    def inverse_bind_matrices(self, transpose: bool) -> List[np.ndarray]:
        # Сначала считаем глобальные преобразования
        global_transforms = self.calculate_global_transforms()

        # Вычисление обратных преобразований (bind poses)
        if transpose:
            return [np.linalg.inv(transform.T) for transform in global_transforms]
        else:
            return [np.linalg.inv(transform) for transform in global_transforms]


def create_rotation_matrix(rotation: Vector3, homogeneous: bool = False) -> np.ndarray:
    # Конвертируем в радианы
    rx, ry, rz = (np.radians(angle) for angle in rotation)

    # Матрицы вращения для каждой оси
    cos_rx, sin_rx = np.cos(rx), np.sin(rx)
    Rx = np.array([[1, 0, 0], [0, cos_rx, -sin_rx], [0, sin_rx, cos_rx]])

    cos_ry, sin_ry = np.cos(ry), np.sin(ry)
    Ry = np.array([[cos_ry, 0, sin_ry], [0, 1, 0], [-sin_ry, 0, cos_ry]])

    cos_rz, sin_rz = np.cos(rz), np.sin(rz)
    Rz = np.array([[cos_rz, -sin_rz, 0], [sin_rz, cos_rz, 0], [0, 0, 1]])

    # Общая матрица вращения (Z * Y * X)
    rotation_matrix = Rz @ Ry @ Rx

    # Преобразуем в однородную матрицу 4x4
    if homogeneous:
        homogeneous_matrix = np.eye(4)
        homogeneous_matrix[:3, :3] = rotation_matrix
        return homogeneous_matrix

    return rotation_matrix


def create_transform_matrix(bone: SkeletonBone) -> np.ndarray:
    transform = np.eye(4)
    transform[:3, :3] = create_rotation_matrix(bone.rotation)
    transform[:3, 3] = list(bone.position)

    return transform
