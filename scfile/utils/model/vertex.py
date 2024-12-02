from dataclasses import dataclass, field

from .data import Texture, Vector


@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    normals: Vector = field(default_factory=Vector)
    link: dict[int, float] = field(default_factory=dict)
