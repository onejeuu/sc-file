"""
Dataclasses for scene of 3D models.
"""

from dataclasses import dataclass, field
from typing import TypeAlias

from .animation import ModelAnimation
from .flags import Flag
from .mesh import ModelMesh
from .skeleton import ModelSkeleton


ModelFlags: TypeAlias = dict[Flag, bool]


@dataclass
class SceneScales:
    """Multiplier values for scene components."""

    position: float = 1.0
    uv: float = 1.0
    uv2: float = 1.0
    filtering: float = 0.1


@dataclass
class SceneCounts:
    """Quantifying of scene elements."""

    meshes: int = 0
    bones: int = 0
    clips: int = 0


@dataclass
class ModelScene:
    """Complete 3D model container with geometry, skeleton and animation."""

    scale: SceneScales = field(default_factory=SceneScales)
    count: SceneCounts = field(default_factory=SceneCounts)

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

    def invert_v_textures(self):
        for mesh in self.meshes:
            mesh.textures[:, 1] *= -1

    def flip_v_textures(self):
        for mesh in self.meshes:
            mesh.textures[:, 1] = 1.0 - mesh.textures[:, 1]
