from dataclasses import dataclass, field
from typing import Dict, List

from scfile.consts import McsaModel, Normalization


def scaled_i16(i: float, scale: float) -> float:
    return (i * scale) / Normalization.XYZ_FACTOR

def scaled_u16(i: float, scale: float) -> float:
    return (i * scale) / Normalization.WEIGHT_FACTOR


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0
    w: float = 1.0

@dataclass
class Curve:
    u: float = 0.0
    v: float = 0.0

@dataclass
class Normals:
    i: float = 0.0
    j: float = 0.0
    k: float = 0.0

@dataclass
class VertexBone:
    ids: Dict[int, int] = field(default_factory=dict)
    weights: Dict[int, float] = field(default_factory=dict)

@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    curve: Curve = field(default_factory=Curve)
    normals: Normals = field(default_factory=Normals)
    bone: VertexBone = field(default_factory=VertexBone)

@dataclass
class Polygon:
    v1: int = 0
    v2: int = 0
    v3: int = 0

@dataclass
class Mesh:
    name: bytes = b"name"
    material: bytes = b"material"
    link_count: int = 0
    vertices: List[Vertex] = field(default_factory=list)
    polygons: List[Polygon] = field(default_factory=list)

    def resize_vertices(self, count: int):
        self.vertices = [Vertex() for _ in range(count)]

    def resize_polygons(self, count: int):
        self.polygons = [Polygon() for _ in range(count)]

@dataclass
class Bone:
    name: bytes = b"bone"
    parent_id: int = McsaModel.ROOT_BONE_ID
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)

@dataclass
class Skeleton:
    bones: List[Bone] = field(default_factory=list)

@dataclass
class Model:
    meshes: List[Mesh] = field(default_factory=list)
    skeleton: Skeleton = field(default_factory=Skeleton)
