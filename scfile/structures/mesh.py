"""
Dataclasses for 3D model geometry.
"""

from dataclasses import dataclass, field
from typing import NewType, TypeAlias

import numpy as np

from .vectors import LinksIds, LinksWeights, Polygons, Vector2D, Vector3D


LocalBoneId = NewType("LocalBoneId", int)
SkeletonBoneId = NewType("SkeletonBoneId", int)

BonesMapping: TypeAlias = dict[LocalBoneId, SkeletonBoneId]


@dataclass
class MeshCounts:
    vertices: int = 0
    polygons: int = 0
    links: int = 0
    bones: int = 0


@dataclass
class ModelMesh:
    name: str = "name"
    material: str = "material"

    count: MeshCounts = field(default_factory=MeshCounts)
    bones: BonesMapping = field(default_factory=dict)

    positions: Vector3D = field(default_factory=lambda: np.empty((0, 3), dtype=np.float32))
    textures: Vector2D = field(default_factory=lambda: np.empty((0, 2), dtype=np.float32))
    normals: Vector3D = field(default_factory=lambda: np.empty((0, 3), dtype=np.float32))

    links_ids: LinksIds = field(default_factory=lambda: np.empty((0, 4), dtype=np.uint8))
    links_weights: LinksWeights = field(default_factory=lambda: np.empty((0, 4), dtype=np.float32))

    polygons: Polygons = field(default_factory=lambda: np.empty((0, 3), dtype=np.uint32))
