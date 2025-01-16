from dataclasses import dataclass, field

from .vector import Texture, Vector3


@dataclass
class Vertex:
    position: Vector3 = field(default_factory=Vector3)
    texture: Texture = field(default_factory=Texture)
    normals: Vector3 = field(default_factory=Vector3)

    bone_ids: list[int] = field(default_factory=list)
    bone_weights: list[int] = field(default_factory=list)
