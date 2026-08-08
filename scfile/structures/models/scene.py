"""
Data structures for scenes.
"""

from dataclasses import dataclass, field

from . import features
from .animation import ModelAnimation
from .enums import Feature
from .mesh import ModelMesh
from .skeleton import ModelSkeleton
from .types import InverseBindMatrices


@dataclass
class SceneScales:
    """Scale multipliers for scene data."""

    position: float = 1.0
    uv: float = 1.0
    uv2: float = 1.0


@dataclass
class ModelSkin:
    """Bind matrices used by meshes in an assembled scene."""

    bind_matrices: InverseBindMatrices


@dataclass
class ModelScene:
    """Container for meshes, skeleton, and animation."""

    scale: SceneScales = field(default_factory=SceneScales)

    meshes: list[ModelMesh] = field(default_factory=list)
    skins: list[ModelSkin] = field(default_factory=list)
    skeleton: ModelSkeleton = field(default_factory=ModelSkeleton)
    animation: ModelAnimation = field(default_factory=ModelAnimation)

    def has(
        self,
        feature: Feature,
    ) -> bool:
        """Return whether scene contains a feature."""

        return features.has(self, feature)

    @property
    def total_vertices(self) -> int:
        return sum(len(mesh.vertices) for mesh in self.meshes)

    @property
    def total_polygons(self) -> int:
        return sum(len(mesh.polygons) for mesh in self.meshes)
