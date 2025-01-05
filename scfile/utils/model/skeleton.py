from dataclasses import dataclass, field
from typing import Dict, List, Self

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
