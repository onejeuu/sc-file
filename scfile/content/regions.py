"""World region structures."""

from dataclasses import dataclass, field
from uuid import UUID


type Vector3 = tuple[float, float, float]
type Matrix3 = tuple[Vector3, Vector3, Vector3]


@dataclass
class ChunkHeader:
    """Fields at the start of a compressed chunk."""

    stream_length: int
    section_mask: int
    add_mask: int
    terrain_size: int
    compressed_size: int
    chunk_key: bytes = b""


@dataclass
class ChunkSection:
    """Vertical section of a world chunk."""

    y: int
    blocks: memoryview
    metadata: memoryview = field(default_factory=lambda: memoryview(b""))
    additions: memoryview = field(default_factory=lambda: memoryview(b""))


@dataclass
class RegionChunk:
    """Decompressed world chunk."""

    index: int
    header: ChunkHeader
    payload: bytes
    sections: tuple[ChunkSection, ...] = ()
    lighting: memoryview = field(default_factory=lambda: memoryview(b""))
    biomes: memoryview = field(default_factory=lambda: memoryview(b""))
    records: memoryview = field(default_factory=lambda: memoryview(b""))
    header_raw: bytes = b""
    compressed: bytes = b""
    objects_size: int = 0
    objects_compressed: bytes = b""
    objects_payload: bytes = b""
    record_list: "ChunkRecords | None" = None
    objects: "ChunkObjects | None" = None


@dataclass(frozen=True)
class ChunkRecord:
    """Carpenters wire fields and their original bytes."""

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
    """Records decoded from a chunk, with an optional parsing error."""

    count: int | None = None
    records: tuple[ChunkRecord, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class ObjectHeader:
    """Common object header. type_id is a registry ID in v6, a hash in v7."""

    type_id: int
    flags: int
    flags2: int
    group: UUID | None


@dataclass(frozen=True)
class ObjectPlacement:
    """Object transform; matrix contains three column vectors."""

    uuid: UUID
    matrix: Matrix3
    position: Vector3


@dataclass(frozen=True)
class ObjectSettings:
    """Known instance settings read before behaviour data."""

    active: bool
    activation: int
    feature_flag: str | None
    render_collision_status: int | None
    collision_status: int
    render_model_selection: int
    custom_behaviour: str | None


@dataclass
class ChunkObject:
    """Known prefix of an object. raw retains the entire object entry."""

    index: int
    offset: int
    raw: memoryview
    header: ObjectHeader | None = None
    placement: ObjectPlacement | None = None
    settings: ObjectSettings | None = None
    error: str | None = None


@dataclass
class ChunkObjects:
    """Objects parsed from a length-prefixed container."""

    count: int | None = None
    objects: tuple[ChunkObject, ...] = ()
    error: str | None = None
