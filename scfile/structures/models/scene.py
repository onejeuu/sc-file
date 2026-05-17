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
