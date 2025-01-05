from dataclasses import dataclass, field
from typing import Dict, List, Self

import numpy as np

from scfile.consts import McsaModel

from .data import Vector


ROOT = McsaModel.ROOT_BONE_ID


@dataclass
class SkeletonBone:
    id: int = 0
    name: str = "bone"
    parent_id: int = ROOT
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)
    children: List[Self] = field(default_factory=list)  # TODO: maybe save only ids


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
            # Root bone check
            if bone.parent_id == ROOT:
                roots.append(bone)
                continue

            # Add bone to parents children
            if parent := bone_dict.get(bone.parent_id):
                parent.children.append(bone)

        self.roots = roots
        return roots

    def create_transform_matrix(self, bone: SkeletonBone) -> np.ndarray:
        # Матрица вращения
        rotation_matrix = create_rotation_matrix(bone.rotation)

        # Матрица преобразования 4x4
        transform = np.eye(4)
        transform[:3, :3] = rotation_matrix
        transform[:3, 3] = [bone.position.x, bone.position.y, bone.position.z]

        return transform

    def calculate_global_transforms(self) -> List[np.ndarray]:
        global_transforms = []

        for bone in self.bones:
            local_transform = self.create_transform_matrix(bone)

            if bone.parent_id == ROOT:
                global_transform = local_transform
            else:
                parent_transform = global_transforms[bone.parent_id]
                global_transform = parent_transform @ local_transform

            global_transforms.append(global_transform)

        return global_transforms

    def calculate_bind_poses(self) -> List[np.ndarray]:
        # Сначала считаем глобальные преобразования
        global_transforms = self.calculate_global_transforms()

        # Вычисление обратных преобразований (bind poses)
        return [np.linalg.inv(transform) for transform in global_transforms]


def create_rotation_matrix(rotation: Vector) -> np.ndarray:
    # Конвертируем в радианы
    rx, ry, rz = [np.radians(angle) for angle in rotation]

    # Матрицы вращения для каждой оси
    cos_rx, sin_rx = np.cos(rx), np.sin(rx)
    Rx = np.array([[1, 0, 0], [0, cos_rx, -sin_rx], [0, sin_rx, cos_rx]])

    cos_ry, sin_ry = np.cos(ry), np.sin(ry)
    Ry = np.array([[cos_ry, 0, sin_ry], [0, 1, 0], [-sin_ry, 0, cos_ry]])

    cos_rz, sin_rz = np.cos(rz), np.sin(rz)
    Rz = np.array([[cos_rz, -sin_rz, 0], [sin_rz, cos_rz, 0], [0, 0, 1]])

    # Общая матрица вращения (Z * Y * X)
    return Rz @ Ry @ Rx


def create_transform_matrix(position: Vector, rotation: Vector):
    # Разбиваем на компоненты
    px, py, pz = position
    rx, ry, rz = (np.radians(angle) for angle in rotation)

    # Матрица трансляции
    translation_matrix = np.array([[1, 0, 0, px], [0, 1, 0, py], [0, 0, 1, pz], [0, 0, 0, 1]])

    # Матрицы вращения
    # Вращение вокруг X
    cos_rx, sin_rx = np.cos(rx), np.sin(rx)
    Rx = np.array([[1, 0, 0, 0], [0, cos_rx, -sin_rx, 0], [0, sin_rx, cos_rx, 0], [0, 0, 0, 1]])

    # Вращение вокруг Y
    cos_ry, sin_ry = np.cos(ry), np.sin(ry)
    Ry = np.array([[cos_ry, 0, sin_ry, 0], [0, 1, 0, 0], [-sin_ry, 0, cos_ry, 0], [0, 0, 0, 1]])

    # Вращение вокруг Z
    cos_rz, sin_rz = np.cos(rz), np.sin(rz)
    Rz = np.array([[cos_rz, -sin_rz, 0, 0], [sin_rz, cos_rz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    # Общая матрица вращения (Z * Y * X)
    rotation_matrix = Rz @ Ry @ Rx

    # Итоговая матрица трансформации (Translation * Rotation)
    transform_matrix = translation_matrix @ rotation_matrix

    return transform_matrix
