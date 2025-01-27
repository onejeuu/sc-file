from dataclasses import dataclass, field
from itertools import chain, islice, repeat

from .vectors import Polygon, Vector3
from .vertex import Vertex


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

    local_bones: dict[int, int] = field(default_factory=dict)
    """key: link id, value: bone id"""

    @property
    def bone_indices(self) -> list[str]:
        return [f"{bone_id} {index}" for index, vertex in enumerate(self.vertices) for bone_id in vertex.bone_ids[:1]]

    def allocate_geometry(self) -> None:
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]

    def get_positions(self) -> list[float]:
        return [i for vertex in self.vertices for i in vertex.position]

    def get_textures(self) -> list[float]:
        return [i for vertex in self.vertices for i in vertex.texture]

    def get_normals(self) -> list[float]:
        return [i for vertex in self.vertices for i in vertex.normals]

    def get_bone_ids(self, links: int = 4):
        return [i for v in self.vertices for i in list(islice(chain(v.bone_ids, repeat(0)), links))]

    def get_bone_weights(self, links: int = 4):
        return [i for v in self.vertices for i in list(islice(chain(v.bone_weights, repeat(0.0)), 4))]
