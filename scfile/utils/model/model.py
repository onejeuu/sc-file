from dataclasses import dataclass, field
from typing import List

from scfile.utils.model.mesh import Mesh
from scfile.utils.model.skeleton import Skeleton


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
    flags: Flags = field(default_factory=Flags)
    scale: Scale = field(default_factory=Scale)
    meshes: List[Mesh] = field(default_factory=list)
    skeleton: Skeleton = field(default_factory=Skeleton)

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
