from dataclasses import dataclass, field
from typing import Dict, List, Self

from scfile.consts import McsaModel
from scfile.utils.model.datatypes import Vector


ROOT = McsaModel.ROOT_BONE_ID


@dataclass
class Bone:
    id: int = 0
    name: str = "bone"
    parent_id: int = ROOT
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)
    children: List[Self] = field(default_factory=list)


@dataclass
class Local:
    scale: float = 1.0
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)


@dataclass
class Skeleton:
    bones: List[Bone] = field(default_factory=list)

    def convert_to_local(self):
        """Update bones positions by their parent bone."""

        parent_id = 0
        bones = self.bones

        for bone in bones:
            bone.rotation = Vector()
            parent_id = bone.parent_id

            while parent_id > ROOT:
                parent = bones[parent_id]
                bone.position -= parent.position
                parent_id = parent.parent_id

    def build_hierarchy(self):
        """Fills bones children list."""

        # Create a dictionary to map bone id to bones
        bone_dict: Dict[int, Bone] = {bone.id: bone for bone in self.bones}

        # Find the root bones (those without a parent)
        root_bones: List[Bone] = []

        # Assign children to their respective parents
        for bone in self.bones:
            if bone.parent_id == ROOT:
                root_bones.append(bone)
                continue

            parent_bone = bone_dict.get(bone.parent_id)
            if parent_bone:
                parent_bone.children.append(bone)

        return root_bones
