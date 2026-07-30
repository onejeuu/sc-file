"""
Data structures for scenes.
"""

from dataclasses import dataclass, field

from . import features
from .animation import ModelAnimation
from .enums import Feature
from .mesh import ModelMesh
from .skeleton import ModelSkeleton


@dataclass
class SceneScales:
    """Scale multipliers for scene data."""

    position: float = 1.0
    uv: float = 1.0
    uv2: float = 1.0


@dataclass
class ModelScene:
    """Container for meshes, skeleton, and animation."""

    scale: SceneScales = field(default_factory=SceneScales)

    meshes: list[ModelMesh] = field(default_factory=list)
    skeleton: ModelSkeleton = field(default_factory=ModelSkeleton)
    animation: ModelAnimation = field(default_factory=ModelAnimation)

    def has(
        self,
        feature: Feature,
    ) -> bool:
        """Return whether scene contains a feature."""

        return features.has(self, feature)

    @property
    def total_vertices(self):
        return sum(len(mesh.vertices) for mesh in self.meshes)

    @property
    def total_polygons(self):
        return sum(len(mesh.polygons) for mesh in self.meshes)
