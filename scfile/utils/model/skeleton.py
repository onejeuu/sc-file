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
    bones: List[Bone] = field(default_factory=list)

    def convert_to_local(self):
        """Update bones positions by their parent bone."""

        bones = self.bones
        parent_id = 0

        for bone in bones:
            parent_id = bone.parent_id

            while parent_id > McsaModel.ROOT_BONE_ID:
                parent = bones[parent_id]

                bone.position -= parent.position
                parent_id = parent.parent_id
