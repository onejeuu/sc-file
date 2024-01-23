from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Self

from scfile.consts import Factor, McsaModel
from scfile.utils.mcsa.scale import rescale


class VertexData(ABC):
    @abstractmethod
    def rescale(self, scale: float) -> Self:
        ...

    @classmethod
    def load(cls, *args, scale: float) -> Self:
        return cls(*args).rescale(scale)


@dataclass
class Vector(VertexData):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def rescale(self, scale: float) -> Self:
        self.x, self.y, self.z = rescale(self.x, self.y, self.z, scale=scale, factor=Factor.XYZ)
        return self

@dataclass
class Texture(VertexData):
    u: float = 0.0
    v: float = 0.0

    def rescale(self, scale: float) -> Self:
        self.u, self.v = rescale(self.u, self.v, scale=scale, factor=Factor.UV)
        return self

@dataclass
class Normals(VertexData):
    i: float = 0.0
    j: float = 0.0
    k: float = 0.0

    def rescale(self, scale: float) -> Self:
        self.i, self.j, self.k = rescale(self.i, self.j, self.k, scale=scale, factor=Factor.NORMALS)
        return self

@dataclass
class VertexBone:
    ids: Dict[int, int] = field(default_factory=dict)
    weights: Dict[int, float] = field(default_factory=dict)

@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    normals: Normals = field(default_factory=Normals)
    bone: VertexBone = field(default_factory=VertexBone)

@dataclass
class Polygon:
    v1: int = 0
    v2: int = 0
    v3: int = 0

@dataclass
class Count:
    links: int = 0
    bones: int = 0
    vertices: int = 0
    polygons: int = 0

@dataclass
class Mesh:
    name: str = "name"
    material: str = "material"
    count: Count = field(default_factory=Count)
    vertices: List[Vertex] = field(default_factory=list)
    polygons: List[Polygon] = field(default_factory=list)
    bones: Dict[int, int] = field(default_factory=dict)

    def resize(self):
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]

    def load_position(self, data: Any, scale: float):
        for vertex, (x, y, z, _) in zip(self.vertices, data):
            vertex.position = Vector.load(x, y, z, scale=scale)

    def load_texture(self, data: Any, scale: float):
        for vertex, (u, v) in zip(self.vertices, data):
            vertex.texture = Texture.load(u, v, scale=scale)

    def load_normals(self, data: Any, scale: float):
        for vertex, (i, j, k, _) in zip(self.vertices, data):
            vertex.normals = Normals.load(i, j, k, scale=scale)

    def load_polygons(self, data: Any):
        for polygon, (v1, v2, v3) in zip(self.polygons, data):
            # In obj vertex indexes starts with 1, but in mcsa with 0.
            # So we increase each one by one.
            polygon.v1 = v1 + 1
            polygon.v2 = v2 + 1
            polygon.v3 = v3 + 1

@dataclass
class Bone:
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)

@dataclass
class Skeleton:
    bones: List[Bone] = field(default_factory=list)

@dataclass
class Scale:
    position: float = 1.0
    texture: float = 1.0
    normals: float = 1.0
    bones: float = 1.0

@dataclass
class Model:
    meshes: List[Mesh] = field(default_factory=list)
    skeleton: Skeleton = field(default_factory=Skeleton)
    scale: Scale = field(default_factory=Scale)
