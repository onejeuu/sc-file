"""
Dataclasses for 3D model geometry.
"""

import itertools
from dataclasses import dataclass, field
from itertools import chain, islice, repeat
from typing import Iterable, NewType, TypeAlias

from .vectors import Polygon, Vector3
from .vertex import Vertex


LocalBoneId = NewType("LocalBoneId", int)
SkeletonBoneId = NewType("SkeletonBoneId", int)

BonesMapping: TypeAlias = dict[LocalBoneId, SkeletonBoneId]


@dataclass
class MeshCounts:
    max_links: int = 0
    local_bones: int = 0
    vertices: int = 0
    polygons: int = 0


@dataclass
class MeshDefault:
    rotation: Vector3 = field(default_factory=Vector3)
    position: Vector3 = field(default_factory=Vector3)
    scale: float = 1.0


@dataclass
class ModelMesh:
    name: str = "name"
    material: str = "material"

    count: MeshCounts = field(default_factory=MeshCounts)
    default: MeshDefault = field(default_factory=MeshDefault)

    vertices: list[Vertex] = field(default_factory=list)
    polygons: list[Polygon] = field(default_factory=list)
    faces: list[Polygon] = field(default_factory=list)

    bones_mapping: BonesMapping = field(default_factory=dict)
    """key: local bone id, value: skeleton bone id"""

    def allocate_geometry(self) -> None:
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]

    def get_positions(self) -> list[float]:
        return [i for vertex in self.vertices for i in vertex.position]

    def get_textures(self) -> list[float]:
        return [i for vertex in self.vertices for i in vertex.texture]

    def get_normals(self) -> list[float]:
        return [i for vertex in self.vertices for i in vertex.normals]

    def get_polygons(self) -> list[float]:
        return [i for p in self.polygons for i in p]

    def get_faces(self) -> list[float]:
        return [i for f in self.faces for i in f]

    def get_bone_ids(self, max_links: int):
        return [i for v in self.vertices for i in padded(v.bone_ids, max_links, default=0)]

    def get_bone_weights(self, max_links: int):
        return [i for v in self.vertices for i in padded(v.bone_weights, max_links, default=0.0)]

    def get_bone_indices(self, max_links: int) -> list[str]:
        weight_index = itertools.count()
        return [
            f"{bone_id} {next(weight_index)}"
            for vertex in self.vertices
            for bone_id in padded(vertex.bone_ids, max_links, default=0)
        ]


def padded(data: Iterable[int], stop: int, default: float):
    return list(islice(chain(data, repeat(default)), stop))
