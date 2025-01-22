from dataclasses import dataclass, field

from .vectors import Polygon, Vector3
from .vertex import Vertex


@dataclass
class MeshCounts:
    max_links: int = 0
    bones: int = 0
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
    global_polygons: list[Polygon] = polygons

    bones: dict[int, int] = field(default_factory=dict)
    """key: link id, value: bone id"""

    @property
    def bone_indices(self):
        return [f"{bone_id} {index}" for index, vertex in enumerate(self.vertices) for bone_id in vertex.bone_ids[:1]]

    def allocate_geometry(self) -> None:
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]
