"""
Dataclasses for scene of 3D models.
"""

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Annotated, List, NewType, Self, TypeAlias

import numpy as np
from numpy.typing import NDArray

from scfile.consts import McsaModel


class FlagKey(StrEnum):
    SKELETON = auto()
    UV = auto()
    UV2 = auto()
    NORMALS = auto()
    TANGENTS = auto()
    COLORS = auto()


class UVOrigin(StrEnum):
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()


class SkeletonSpace(StrEnum):
    GLOBAL = auto()
    LOCAL = auto()


Flag = FlagKey
ModelFlags: TypeAlias = dict[Flag, bool]

Vector2D: TypeAlias = Annotated[NDArray[np.float32], (..., 2)]
Vector3D: TypeAlias = Annotated[NDArray[np.float32], (..., 3)]
Vector4D: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
LinksIds: TypeAlias = Annotated[NDArray[np.uint8], (..., 4)]
LinksWeights: TypeAlias = Annotated[NDArray[np.float32], (..., 4)]
Links: TypeAlias = tuple[LinksIds, LinksWeights]
Polygons: TypeAlias = Annotated[NDArray[np.uint32], (..., 3)]

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
class BoundingBox:
    min: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    max: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    radius: float = 0.0


@dataclass
class ModelMesh:
    """3D mesh geometry container."""

    name: str = "name"
    material: str = "material"

    count: MeshCounts = field(default_factory=MeshCounts)
    bounds: BoundingBox = field(default_factory=BoundingBox)
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

    uv1_origin: UVOrigin = UVOrigin.TOP_LEFT
    uv2_origin: UVOrigin = UVOrigin.TOP_LEFT


@dataclass
class SkeletonBone:
    """Single skeleton bone with transform data."""

    id: int = 0
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID

    position: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    rotation: Vector3D = field(default_factory=lambda: np.zeros(3, dtype=np.float32))

    children: List[Self] = field(default_factory=list, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent_id == McsaModel.ROOT_BONE_ID

    @property
    def quaternion(self) -> Vector4D:
        return euler_to_quat(self.rotation)

    @property
    def slug(self) -> str:
        return "".join(ch for ch in self.name.lower() if ch.isalnum())


@dataclass
class ModelSkeleton:
    """Skeleton bones container."""

    bones: List[SkeletonBone] = field(default_factory=list)
    space: SkeletonSpace = SkeletonSpace.GLOBAL

    @property
    def roots(self) -> List[SkeletonBone]:
        return list(filter(lambda bone: bone.is_root, self.bones))

    def convert_to_local(self) -> None:
        for bone in self.bones:
            parent_id = bone.parent_id

            # Convert global position to parent-relative space
            while parent_id > McsaModel.ROOT_BONE_ID:
                parent = self.bones[parent_id]
                bone.position -= parent.position  # Make position relative to parent
                parent_id = parent.parent_id  # Move up hierarchy

    def build_hierarchy(self) -> None:
        # Rebuild hierarchy
        for bone in self.bones:
            if not bone.is_root:
                parent = self.bones[bone.parent_id]
                parent.children.append(bone)

    def calculate_global_transforms(self) -> list[np.ndarray]:
        transforms: list[np.ndarray] = []

        for bone in self.bones:
            local_matrix = create_transform_matrix(bone.position, bone.rotation)
            global_matrix = local_matrix if bone.is_root else transforms[bone.parent_id] @ local_matrix
            transforms.append(global_matrix)

        return transforms

    def inverse_bind_matrices(self, transpose: bool) -> np.ndarray:
        global_transforms = self.calculate_global_transforms()

        inverse_matrices = [np.linalg.inv(matrix) for matrix in global_transforms]

        if transpose:
            inverse_matrices = [matrix.T for matrix in inverse_matrices]

        return np.array(inverse_matrices, dtype=np.float32)


def create_rotation_matrix(rotation: Vector3D) -> np.ndarray:
    angles = np.radians(rotation)
    cx, cy, cz = np.cos(angles)
    sx, sy, sz = np.sin(angles)

    return np.array(
        [
            [cy * cz, -cy * sz, sy],
            [cx * sz + cz * sx * sy, cx * cz - sx * sy * sz, -cy * sx],
            [sx * sz - cx * cz * sy, cz * sx + cx * sy * sz, cx * cy],
        ],
        dtype=np.float32,
    )


def create_transform_matrix(position: Vector3D, rotation: Vector3D) -> np.ndarray:
    matrix = np.eye(4, dtype=np.float32)
    matrix[:3, :3] = create_rotation_matrix(rotation)
    matrix[:3, 3] = position
    return matrix


def euler_to_quat(rotation: Vector3D, degrees: bool = True) -> Vector4D:
    x, y, z = np.radians(rotation) if degrees else rotation
    hx, hy, hz = x * 0.5, y * 0.5, z * 0.5

    cx, cy, cz = np.cos([hx, hy, hz])
    sx, sy, sz = np.sin([hx, hy, hz])

    return np.array(
        [
            sx * cy * cz - cx * sy * sz,
            cx * sy * cz + sx * cy * sz,
            cx * cy * sz - sx * sy * cz,
            cx * cy * cz + sx * sy * sz,
        ],
        dtype=np.float32,
    )


@dataclass
class AnimationClip:
    """Single animation clip with timing and transformation data."""

    name: str = "clip"
    frames: int = 0
    rate: float = 0.33
    transforms: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.float32))

    @property
    def times(self):
        return np.arange(self.frames, dtype=np.float32) * self.rate


@dataclass
class ModelAnimation:
    """Animation clips container."""

    clips: list[AnimationClip] = field(default_factory=list)

    def convert_to_local(self, skeleton: ModelSkeleton):
        for clip in self.clips:
            for bone in skeleton.bones:
                clip.transforms[:, bone.id, 4:7] += bone.position


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
            mesh.uv1[:, 1] *= -1
            mesh.uv2[:, 1] *= -1

    def flip_v_textures(self):
        for mesh in self.meshes:
            mesh.uv1[:, 1] = 1.0 - mesh.uv1[:, 1]
            mesh.uv2[:, 1] = 1.0 - mesh.uv2[:, 1]

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
