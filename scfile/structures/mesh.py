"""
Dataclasses for 3D model geometry.
"""

from dataclasses import dataclass, field
from typing import NewType, TypeAlias

import numpy as np

from .vectors import LinksIds, LinksWeights, Polygons, Vector2D, Vector3D


LocalBoneId = NewType("LocalBoneId", int)  # Bone id within local mesh scope
SkeletonBoneId = NewType("SkeletonBoneId", int)  # Bone id within skeleton hierarchy

BonesMapping: TypeAlias = dict[LocalBoneId, SkeletonBoneId]  # Mapping between local and skeleton ids


@dataclass
class MeshCounts:
    """Quantifying of mesh elements."""

    vertices: int = 0
    polygons: int = 0
    links: int = 0
    bones: int = 0


@dataclass
class MeshOrigin:
    position: Vector3D = field(default_factory=lambda: np.empty(3, dtype=np.float32))
    rotation: Vector3D = field(default_factory=lambda: np.empty(3, dtype=np.float32))
    scale: float = 0.0


@dataclass
class ModelMesh:
    """3D mesh geometry container."""

    name: str = "name"
    material: str = "material"

    count: MeshCounts = field(default_factory=MeshCounts)
    origin: MeshOrigin = field(default_factory=MeshOrigin)

    bones: BonesMapping = field(default_factory=dict)

    positions: Vector3D = field(default_factory=lambda: np.empty((0, 3), dtype=np.float32))
    textures: Vector2D = field(default_factory=lambda: np.empty((0, 2), dtype=np.float32))
    normals: Vector3D = field(default_factory=lambda: np.empty((0, 3), dtype=np.float32))

    links_ids: LinksIds = field(default_factory=lambda: np.empty((0, 4), dtype=np.uint8))
    links_weights: LinksWeights = field(default_factory=lambda: np.empty((0, 4), dtype=np.float32))

    polygons: Polygons = field(default_factory=lambda: np.empty((0, 3), dtype=np.uint32))
