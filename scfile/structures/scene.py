from collections import defaultdict
from dataclasses import dataclass, field
from typing import TypeAlias

from .anim import ModelAnimation
from .mesh import ModelMesh
from .skeleton import ModelSkeleton


ModelFlags: TypeAlias = defaultdict[int, bool]


@dataclass
class SceneScales:
    position: float = 1.0
    texture: float = 1.0
    normals: float = 1.0
    filtering: float = 0.1


@dataclass
class ModelScene:
    scale: SceneScales = field(default_factory=SceneScales)
    meshes: list[ModelMesh] = field(default_factory=list)
    skeleton: ModelSkeleton = field(default_factory=ModelSkeleton)
    animation: ModelAnimation = field(default_factory=ModelAnimation)

    @property
    def total_vertices(self):
        return sum(mesh.count.vertices for mesh in self.meshes)

    @property
    def total_polygons(self):
        return sum(mesh.count.polygons for mesh in self.meshes)

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

    def convert_polygons_to_faces(self, start_index: int = 0):
        """Updates meshes faces indexes."""
        offset = start_index

        for mesh in self.meshes:
            mesh.faces = [polygon >> offset for polygon in mesh.polygons]
            offset += mesh.count.vertices

    def invert_v_textures(self):
        for mesh in self.meshes:
            for vertex in mesh.vertices:
                vertex.texture.v *= -1

    def flip_v_textures(self):
        for mesh in self.meshes:
            for vertex in mesh.vertices:
                vertex.texture.v = 1.0 - vertex.texture.v

    def get_vertices(self):
        return [v for mesh in self.meshes for v in mesh.vertices]
