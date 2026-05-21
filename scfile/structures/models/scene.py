from dataclasses import dataclass, field

from .animation import ModelAnimation
from .mesh import ModelMesh
from .skeleton import ModelSkeleton


@dataclass
class SceneScales:
    """Multiplier values for scene components."""

    position: float = 1.0
    uv: float = 1.0
    uv2: float = 1.0
    filtering: float = 0.1


@dataclass
class ModelScene:
    """Complete 3D model container with geometry, skeleton and animation."""

    scale: SceneScales = field(default_factory=SceneScales)

    meshes: list[ModelMesh] = field(default_factory=list)
    skeleton: ModelSkeleton = field(default_factory=ModelSkeleton)
    animation: ModelAnimation = field(default_factory=ModelAnimation)

    @property
    def total_vertices(self):
        return sum(len(mesh.vertices) for mesh in self.meshes)

    @property
    def total_polygons(self):
        return sum(len(mesh.polygons) for mesh in self.meshes)
