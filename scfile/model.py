from dataclasses import dataclass, field
from typing import Dict, List

from scfile.consts import Normalization, ROOT_BONE_ID


def scaled(scale: float, i: float) -> float:
    return scale * i / Normalization.VERTEX_LIMIT


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0


@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    normals: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    bone_count: int = 0
    bone_ids: List[int] = field(default_factory=lambda: [0] * 4)
    bone_weights: List[float] = field(default_factory=lambda: [0.0] * 4)


@dataclass
class Polygon:
    vertex1: int = 0
    vertex2: int = 0
    vertex3: int = 0


@dataclass
class Mesh:
    vertices: List[Vertex] = field(default_factory=lambda: [Vertex()])
    polygons: List[Polygon] = field(default_factory=lambda: [Polygon()])
    name: str = ""
    material: str = ""

    def resize_vertices(self, count: int):
        self.vertices = [Vertex() for _ in range(count)]

    def resize_polygons(self, count: int):
        self.polygons = [Polygon() for _ in range(count)]


@dataclass
class Bone:
    name: str = ""
    parent_id: int = ROOT_BONE_ID
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)


@dataclass
class Skeleton:
    bones: Dict[int, Bone] = field(default_factory=lambda: {0: Bone()})


@dataclass
class Model:
    meshes: Dict[int, Mesh] = field(default_factory=lambda: {0: Mesh()})
    skeleton: Skeleton = field(default_factory=Skeleton)
