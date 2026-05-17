from dataclasses import dataclass, field

import numpy as np

from .enums import LinkSpace, UVOrigin, UVSign
from .types import BonesMapping, LinksIds, LinksWeights, Polygons, Vector2D, Vector3D, Vector4D


@dataclass
class MeshCounts:
    """Quantifying of mesh elements."""

    vertices: int = 0
    polygons: int = 0
    links: int = 0
    bones: int = 0


@dataclass
class MeshBounds:
    min: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    max: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    radius: float = 0.0


@dataclass
class ModelMesh:
    """3D mesh geometry container."""

    name: str = "name"
    material: str = "material"

    count: MeshCounts = field(default_factory=MeshCounts)
    bounds: MeshBounds = field(default_factory=MeshBounds)
    quads: bool = False

    bones: BonesMapping = field(default_factory=dict)

    positions: Vector3D = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))
    uv1: Vector2D = field(default_factory=lambda: np.zeros((0, 2), dtype=np.float32))
    uv2: Vector2D = field(default_factory=lambda: np.zeros((0, 2), dtype=np.float32))
    normals: Vector3D = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))
    tangents: Vector4D = field(default_factory=lambda: np.zeros((0, 4), dtype=np.float32))

    links_ids: LinksIds = field(default_factory=lambda: np.zeros((0, 4), dtype=np.uint8))
    links_weights: LinksWeights = field(default_factory=lambda: np.zeros((0, 4), dtype=np.float32))

    polygons: Polygons = field(default_factory=lambda: np.zeros((0, 3), dtype=np.uint32))

    link_space: LinkSpace = LinkSpace.GLOBAL
    uv_origin: UVOrigin = UVOrigin.TOP_LEFT
    uv_sign: UVSign = UVSign.POSITIVE
