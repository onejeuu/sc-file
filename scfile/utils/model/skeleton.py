from dataclasses import dataclass, field
from typing import List

from scfile.consts import McsaModel
from scfile.utils.model.datatypes import Vector


@dataclass
class Bone:
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)


@dataclass
class Local:
    scale: float = 1.0
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)


@dataclass
class Skeleton:
    # local: Local = field(default_factory=Local)
    bones: List[Bone] = field(default_factory=list)

    def convert_to_local(self):
        """Update bones positions by parent bone."""

        parent_id = 0
        bones = self.bones

        for bone in bones:
            bone.rotation = Vector()
            parent_id = bone.parent_id

            while parent_id >= 0:
                bone.position -= bones[parent_id].position
                parent_id = self.bones[parent_id].parent_id
