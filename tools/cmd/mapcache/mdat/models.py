from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from uuid import UUID


type XZ = tuple[int, int]
type XYZ = tuple[int, int, int]
type Buffer = Literal["file", "terrain", "objects"]


@dataclass(frozen=True)
class Note:
    buffer: Buffer
    offset: int
    message: str


@dataclass(frozen=True)
class Slice:
    offset: int
    size: int
    data: memoryview

    @property
    def end(self) -> int:
        return self.offset + self.size

    @property
    def complete(self) -> bool:
        return self.offset >= 0 and len(self.data) == self.size


def view(data: memoryview, offset: int, size: int) -> Slice:
    raw = data[offset : offset + size] if offset >= 0 and size >= 0 else memoryview(b"")
    return Slice(offset, size, raw)


@dataclass(frozen=True)
class Entry:
    index: int
    sector: int
    sectors: int
    uuid_words: tuple[int, int, int, int]
    raw: Slice

    @property
    def present(self) -> bool:
        return self.sector != 0

    @property
    def uuid(self) -> UUID:
        a, b, c, d = self.uuid_words
        high = ((a & 0xFFFFFFFF) << 32) | (b + 0x80000000)
        low = ((c & 0xFFFFFFFF) << 32) | (d + 0x80000000)
        return UUID(int=(high << 64) | low)


@dataclass(frozen=True)
class Header:
    stream_length: int
    section_mask: int
    add_mask: int
    terrain_size: int
    compressed_size: int

    @property
    def layout_size(self) -> int:
        return (self.section_mask & 0xFFFF).bit_count() * 12288 + (self.add_mask & 0xFFFF).bit_count() * 2048 + 256


@dataclass
class Frame:
    raw: Slice
    data: bytes | None = None


@dataclass
class Chunk:
    entry: Entry
    coordinates: XZ | None
    allocation: Slice
    header_raw: Slice
    header: Header | None = None
    terrain: Frame | None = None
    objects: Frame | None = None
    objects_size: int | None = None
    notes: list[Note] = field(default_factory=list)

    @property
    def physical_size(self) -> int | None:
        if self.header is None or self.objects_size is None:
            return None
        return self.header.compressed_size + self.objects_size + 24


@dataclass(frozen=True)
class Location:
    path: Path
    region: XZ | None
    index: int
    chunk: XZ | None


@dataclass(frozen=True)
class RecordHeader:
    type: int
    position: XYZ


@dataclass(frozen=True)
class RecordPayload:
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


@dataclass(frozen=True)
class Record:
    index: int
    raw: Slice
    header: RecordHeader
    payload: RecordPayload


@dataclass
class Records:
    raw: Slice
    count: int | None = None
    items: list[Record] = field(default_factory=list)
    consumed: int = 0
    stopped: RecordHeader | None = None
    notes: list[Note] = field(default_factory=list)

    @property
    def tail(self) -> Slice:
        return Slice(
            self.raw.offset + self.consumed, len(self.raw.data) - self.consumed, self.raw.data[self.consumed :]
        )


@dataclass(frozen=True)
class ObjectItem:
    index: int
    length_offset: int
    raw: Slice

    @property
    def prefix(self) -> int | None:
        return int.from_bytes(self.raw.data[:2], "big") if len(self.raw.data) >= 2 else None


@dataclass
class Objects:
    raw: memoryview
    count: int | None = None
    items: list[ObjectItem] = field(default_factory=list)
    consumed: int = 0
    notes: list[Note] = field(default_factory=list)

    @property
    def tail(self) -> Slice:
        return view(self.raw, self.consumed, len(self.raw) - self.consumed)


@dataclass(frozen=True)
class Placement:
    uuid: UUID
    matrix_columns: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    position: tuple[float, float, float]
    raw: Slice
    tail: Slice

    def transform(self, point: tuple[float, float, float]) -> tuple[float, float, float]:
        a, b, c = self.matrix_columns
        x, y, z = point
        tx, ty, tz = self.position
        return (
            a[0] * x + b[0] * y + c[0] * z + tx,
            a[1] * x + b[1] * y + c[1] * z + ty,
            a[2] * x + b[2] * y + c[2] * z + tz,
        )


@dataclass(frozen=True)
class State:
    value: int

    @property
    def block_id(self) -> int:
        return self.value & 0xFFF

    @property
    def metadata(self) -> int:
        return self.value >> 12

    @property
    def addition(self) -> int:
        return (self.value >> 8) & 15


@dataclass(frozen=True)
class Sample:
    plane: str
    offset: int | None
    byte: int | None
    value: int | None
    nibble: Literal["low", "high"] | None = None


@dataclass(frozen=True)
class Block:
    local: XYZ
    world: XYZ | None
    section: int
    index: int
    status: Literal["stored", "absent", "unavailable"]
    state: State | None
    samples: tuple[Sample, ...]
