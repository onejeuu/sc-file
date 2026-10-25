"""World region structures."""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class ChunkHeader:
    """Header of compressed world chunk."""

    record_size: int = 0
    section_mask: int = 0
    add_mask: int = 0
    terrain_size: int = 0
    compressed_size: int = 0
    chunk_key: bytes = b""
    objects_size: int = 0


@dataclass
class ChunkSection:
    """Vertical section of world chunk."""

    y: int = 0
    blocks: memoryview = field(default_factory=lambda: memoryview(b""))
    metadata: memoryview = field(default_factory=lambda: memoryview(b""))
    additions: memoryview = field(default_factory=lambda: memoryview(b""))


@dataclass
class RegionChunk:
    """Decompressed world chunk."""

    index: int = 0
    header: ChunkHeader = field(default_factory=ChunkHeader)
    payload: bytes = field(default_factory=bytes)

    sections: tuple[ChunkSection, ...] = ()
    lighting: memoryview = field(default_factory=lambda: memoryview(b""))
    biomes: memoryview = field(default_factory=lambda: memoryview(b""))
    records: memoryview = field(default_factory=lambda: memoryview(b""))
    header_raw: bytes = b""
    compressed: bytes = b""
    objects_compressed: bytes = b""
    objects_payload: bytes = b""
    record_list: "ChunkRecords | None" = None
    objects: "ChunkObjects | None" = None


@dataclass(frozen=True)
class ChunkRecord:
    """Known Carpenters record with its original bytes."""

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
    """Parsed records followed by an uninterpreted remainder."""

    raw: memoryview
    count: int | None = None
    records: tuple[ChunkRecord, ...] = ()
    consumed: int = 0
    error: str | None = None

    @property
    def tail(self) -> memoryview:
        return self.raw[self.consumed:]


@dataclass(frozen=True)
class ObjectHeader:
    """Version-specific identity and common instance flags."""

    network_id: int | None
    type_hash: int | None
    flags: int
    flags2: int
    group: UUID | None
    material_patch: str | None
    client_csv: int | None
    client_cbv: int | None
    instance_serial: int | None


@dataclass(frozen=True)
class ObjectPlacement:
    uuid: UUID
    matrix_columns: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    position: tuple[float, float, float]


@dataclass(frozen=True)
class ObjectSettings:
    active: bool
    activation: int
    feature_flag: str | None
    render_collision_status: int | None
    collision_status: int
    render_model_selection: int
    custom_behaviour: str | None


@dataclass
class ChunkObject:
    """Map object; behaviour-dependent bytes remain available in tail."""

    index: int
    offset: int
    raw: memoryview
    header: ObjectHeader | None = None
    placement: ObjectPlacement | None = None
    settings: ObjectSettings | None = None
    consumed: int = 0
    error: str | None = None

    @property
    def tail(self) -> memoryview:
        return self.raw[self.consumed:]


@dataclass
class ChunkObjects:
    """Length-prefixed map objects and any unparsed container bytes."""

    raw: memoryview
    count: int | None = None
    objects: tuple[ChunkObject, ...] = ()
    consumed: int = 0
    error: str | None = None

    @property
    def tail(self) -> memoryview:
        return self.raw[self.consumed:]
