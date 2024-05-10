from dataclasses import dataclass, field
from typing import Dict, List, Self

from scfile.consts import McsaModel


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __sub__(self, vec: Self):
        return Vector(self.x - vec.x, self.y - vec.y, self.z - vec.z)


@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0


@dataclass
class Polygon:
    a: int = 0
    b: int = 0
    c: int = 0

    def __lshift__(self, offset: int):
        return Polygon(self.a - offset, self.b - offset, self.c - offset)

    def __rshift__(self, offset: int):
        return Polygon(self.a + offset, self.b + offset, self.c + offset)


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

    global_polygons: List[Polygon] = field(default_factory=list)
    """Empty before `convert_polygons_to_global` is called for model."""

    def resize(self) -> None:
        """Fills vertices & polygons by their counts."""
        self.vertices = [Vertex() for _ in range(self.count.vertices)]
        self.polygons = [Polygon() for _ in range(self.count.polygons)]


@dataclass
class Bone:
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)


@dataclass
class Local:
    scale: float = 1.0
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)


@dataclass
class Skeleton:
    # local: Local = field(default_factory=Local)
    bones: List[Bone] = field(default_factory=list)

    def convert_to_local(self):
        parent_id = 0
        bones = self.bones

        for bone in bones:
            bone.rotation = Vector()
            parent_id = bone.parent_id

            while parent_id >= 0:
                bone.position -= bones[parent_id].position
                parent_id = self.bones[parent_id].parent_id


@dataclass
class Flags:
    skeleton: bool = False
    texture: bool = False
    normals: bool = False


@dataclass
class Scale:
    position: float = 1.0
    texture: float = 1.0
    normals: float = 1.0
    weight: float = 1.0


@dataclass
class Model:
    meshes: List[Mesh] = field(default_factory=list)
    skeleton: Skeleton = field(default_factory=Skeleton)
    flags: Flags = field(default_factory=Flags)
    scale: Scale = field(default_factory=Scale)

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

    def convert_polygons_to_global(self, start: int = 0):
        """Updates meshes global_polygons indexes."""
        offset = start

        for mesh in self.meshes:
            for index, polygon in enumerate(mesh.polygons):
                mesh.global_polygons.insert(index, polygon >> offset)
            offset += mesh.count.vertices
