from dataclasses import dataclass, field
from typing import Dict, List

from scfile.utils.model.datatypes import Polygon, Texture, Vector


@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    normals: Vector = field(default_factory=Vector)
    link: Dict[int, float] = field(default_factory=dict)
    """key: bone id, value: weight"""
    # color: Color = field(default_factory=Color)


@dataclass
class Count:
    max_links: int = 0
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
    """key: link id, value: bone id"""

    global_polygons: List[Polygon] = field(default_factory=list)
    """Empty before `convert_polygons_to_global` is called for model."""

    def resize(self) -> None:
        """Fills vertices & polygons by their counts."""
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]
