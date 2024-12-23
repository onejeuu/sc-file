from dataclasses import dataclass, field

from .data import Polygon
from .vertex import Vertex


@dataclass
class MeshCounts:
    max_links: int = 0
    links: int = 0
    bones: int = 0
    vertices: int = 0
    polygons: int = 0


@dataclass
class ModelMesh:
    name: str = "name"
    material: str = "material"

    count: MeshCounts = field(default_factory=MeshCounts)

    vertices: list[Vertex] = field(default_factory=list)

    polygons: list[Polygon] = field(default_factory=list)
    global_polygons: list[Polygon] = polygons

    bones: dict[int, int] = field(default_factory=dict)
    """key: link id, value: bone id"""

    def allocate_geometry(self) -> None:
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]
