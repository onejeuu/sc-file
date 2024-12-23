from dataclasses import dataclass, field

from .data import Texture, Vector


@dataclass
class Joint:
    bone_id: int
    weight: float


@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    normals: Vector = field(default_factory=Vector)

    joints: dict[int, float] = field(default_factory=dict)

    """
    joints: list[Joint] = field(default_factory=list, metadata={"max_length": 4})

    @property
    def primary_bone_id(self):
        if not self.joints:
            return 0

        return max(self.joints, key=lambda j: j.weight).bone_id

    @property
    def normalized_weights(self) -> list[tuple[int, float]]:
        if not self.joints:
            return [(0, 1.0)]

        total_weight = sum(joint.weight for joint in self.joints)
        return [(joint.bone_id, joint.weight / total_weight) for joint in self.joints]
    """
