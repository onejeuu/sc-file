"""World region structures."""

from dataclasses import dataclass, field
from uuid import UUID


type Vector3 = tuple[float, float, float]
type Matrix3 = tuple[Vector3, Vector3, Vector3]


@dataclass
class ChunkHeader:
    """Metadata used to locate terrain data."""

    stream_length: int
    section_mask: int
    add_mask: int
    terrain_size: int
    compressed_size: int
    chunk_key: bytes = b""


@dataclass
class ChunkSection:
    """Vertical voxel layer of a chunk."""

    y: int
    blocks: memoryview
    metadata: memoryview
    additions: memoryview | None = None


@dataclass
class RegionChunk:
    """Decoded terrain with attached entities."""

    index: int
    sections: tuple[ChunkSection, ...]
    biomes: memoryview
    lighting: memoryview
    records: "ChunkRecords | None" = None
    objects: "ChunkObjects | None" = None
    materials: "ChunkTileMaterials | None" = None


@dataclass(frozen=True)
class ChunkRecord:
    """Tile entity at a terrain position."""

    type: int
    position: tuple[int, int, int]
    flags: int
    covers: tuple[int, ...]
    color_short: tuple[int, ...]
    color_exponent: int | None
    overlay: tuple[int, ...]
    rot: int | None
    packcovers: int | None
    ctm_data: tuple[int, ...]
    data: int
    data_ext: int | None
    raw: memoryview


@dataclass
class ChunkRecords:
    """Decoded tile entities with parse status."""

    count: int | None = None
    records: tuple[ChunkRecord, ...] = ()
    error: str | None = None
    raw: memoryview = field(kw_only=True)


@dataclass(frozen=True)
class ObjectHeader:
    """Object definition identity and instance flags."""

    network_id: int
    flags: int
    flags2: int
    group: UUID | None


@dataclass(frozen=True)
class ObjectPlacement:
    """Object position and orientation in world space."""

    uuid: UUID
    matrix: Matrix3
    position: Vector3


@dataclass(frozen=True)
class ObjectSettings:
    """Object rendering state."""

    active: bool
    activation: int
    feature_flag: str | None
    render_collision_status: int | None
    collision_status: int
    render_model_selection: int
    custom_behaviour: str | None


@dataclass
class ChunkObject:
    """Object instance with parsed state and source data."""

    index: int
    offset: int
    header: ObjectHeader | None = None
    placement: ObjectPlacement | None = None
    settings: ObjectSettings | None = None
    error: str | None = None
    raw: memoryview = field(kw_only=True)


@dataclass
class ChunkObjects:
    """Object instances with parse status."""

    count: int | None = None
    objects: tuple[ChunkObject, ...] = ()
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ChunkTileMaterials:
    """Packed material data for block faces."""

    entries: memoryview
    face_map: memoryview
    shape_data: memoryview
    record_types: memoryview
