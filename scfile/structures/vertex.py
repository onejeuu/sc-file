"""
Dataclasses for 3D model vertex.
"""

from dataclasses import dataclass, field

from .vectors import Vector2, Vector3


@dataclass
class Vertex:
    position: Vector3 = field(default_factory=Vector3)
    texture: Vector2 = field(default_factory=Vector2)
    normals: Vector3 = field(default_factory=Vector3)

    bone_ids: list[int] = field(default_factory=list)
    bone_weights: list[int] = field(default_factory=list)
