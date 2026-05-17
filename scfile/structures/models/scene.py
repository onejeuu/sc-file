from dataclasses import dataclass, field

import numpy as np

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

    def normalize_vectors(self):
        for mesh in self.meshes:
            if mesh.normals is not None and mesh.normals.size > 0:
                norm = np.linalg.norm(mesh.normals, axis=1, keepdims=True)
                mesh.normals = np.divide(mesh.normals, norm, out=np.zeros_like(mesh.normals), where=norm != 0)

            if mesh.tangents is not None and mesh.tangents.size > 0:
                xyz = mesh.tangents[:, :3]
                norm = np.linalg.norm(xyz, axis=1, keepdims=True)
                normalized_xyz = np.divide(xyz, norm, out=np.zeros_like(xyz), where=norm != 0)
                mesh.tangents[:, :3] = normalized_xyz
