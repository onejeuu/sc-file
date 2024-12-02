from dataclasses import dataclass, field

from .mesh import ModelMesh
from .skeleton import ModelSkeleton


@dataclass
class SceneScales:
    position: float = 1.0
    texture: float = 1.0
    normals: float = 1.0
    weight: float = 1.0


@dataclass
class ModelScene:
    scale: SceneScales = field(default_factory=SceneScales)
    meshes: list[ModelMesh] = field(default_factory=list)
    skeleton: ModelSkeleton = field(default_factory=ModelSkeleton)

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

    def convert_polygons_to_global(self, start_index: int = 0):
        """Updates meshes global_polygons indexes."""
        offset = start_index

        for mesh in self.meshes:
            mesh.global_polygons = [polygon >> offset for polygon in mesh.polygons]
            offset += mesh.count.vertices
