from dataclasses import dataclass, field
from typing import Dict, List

from scfile.consts import McsaModel


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def sub(self, vec):
        self.x -= vec.x
        self.y -= vec.y
        self.z -= vec.z

@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0


@dataclass
class Polygon:
    a: int = 0
    b: int = 0
    c: int = 0


@dataclass
class Color:
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0


@dataclass
class VertexBone:
    ids: Dict[int, int] = field(default_factory=dict)
    weights: Dict[int, float] = field(default_factory=dict)


@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    normals: Vector = field(default_factory=Vector)
    bone: VertexBone = field(default_factory=VertexBone)
    # color: Color = field(default_factory=Color)


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

    @property
    def offset(self) -> int:
        return len(self.vertices)

    def resize(self) -> None:
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]


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
class Flags:
    texture: bool = False
    normals: bool = False


@dataclass
class Scale:
    position: float = 1.0
    texture: float = 1.0
    normals: float = 1.0
    weight: float = 1.0


@dataclass
class Local:
    axis: Vector = field(default_factory=Vector)
    center: Vector = field(default_factory=Vector)


@dataclass
class Model:
    meshes: List[Mesh] = field(default_factory=list)
    skeleton: Skeleton = field(default_factory=Skeleton)
    flags: Flags = field(default_factory=Flags)
    scale: Scale = field(default_factory=Scale)
    # local: Local = field(default_factory=Local)

    def ensure_unique_names(self):
        """Updates meshes names, excluding repetitions."""
        seen_names: set[str] = set()

        for mesh in self.meshes:
            name = mesh.name or "noname"

            base_name, count = name, 2
            unique_name = f"{base_name}"

            while unique_name in seen_names:
                unique_name = f"{base_name}_{count}"
                count += 1

            mesh.name = unique_name
            seen_names.add(unique_name)
