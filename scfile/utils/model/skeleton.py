from dataclasses import dataclass, field
from math import cos, radians, sin
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
    children: List[Self] = field(default_factory=list)


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


def create_translation_matrix(position: Vector) -> np.ndarray:
    matrix = np.eye(4)
    matrix[0, 3] = position.x
    matrix[1, 3] = position.y
    matrix[2, 3] = position.z
    return matrix


def create_rotation_matrix(rotation: Vector) -> np.ndarray:
    # Convert degrees to radians
    rx, ry, rz = map(radians, rotation)

    # Rotation matrix around X
    Rx = np.array([[1, 0, 0, 0], [0, cos(rx), -sin(rx), 0], [0, sin(rx), cos(rx), 0], [0, 0, 0, 1]])

    # Rotation matrix around Y
    Ry = np.array([[cos(ry), 0, sin(ry), 0], [0, 1, 0, 0], [-sin(ry), 0, cos(ry), 0], [0, 0, 0, 1]])

    # Rotation matrix around Z
    Rz = np.array([[cos(rz), -sin(rz), 0, 0], [sin(rz), cos(rz), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    return Rz @ Ry @ Rx


def calculate_bone_matrix(bone: SkeletonBone) -> np.ndarray:
    translation = create_translation_matrix(bone.position)
    rotation = create_rotation_matrix(bone.rotation)
    return translation @ rotation


def calculate_global_matrix(bone: SkeletonBone, skeleton: ModelSkeleton) -> np.ndarray:
    local_matrix = calculate_bone_matrix(bone)

    if bone.parent_id >= 0:
        parent = next((b for b in skeleton.bones if b.id == bone.parent_id), None)
        if parent:
            parent_global = calculate_global_matrix(parent, skeleton)
            return parent_global @ local_matrix

    return local_matrix


def get_bone_martix(bone: SkeletonBone, skeleton: ModelSkeleton) -> str:
    matrix = calculate_global_matrix(bone, skeleton)
    return " ".join(map(str, matrix.T.flatten()))
