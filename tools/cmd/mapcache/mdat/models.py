import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from uuid import UUID

from scfile.content import regions as S


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
    key: bytes
    raw: Slice

    @property
    def present(self) -> bool:
        return self.sector != 0

    @property
    def uuid(self) -> UUID | None:
        if len(self.key) != 16:
            return None
        a, b, c, d = struct.unpack(">4i", self.key)
        high = ((a & 0xFFFFFFFF) << 32) | (b + 0x80000000)
        low = ((c & 0xFFFFFFFF) << 32) | (d + 0x80000000)
        return UUID(int=(high << 64) | low)


class Header(S.ChunkHeader):
    @property
    def layout_size(self) -> int:
        return (self.section_mask & 0xFFFF).bit_count() * 12288 + (self.addition_mask & 0xFFFF).bit_count() * 2048 + 256


@dataclass
class Frame:
    raw: Slice
    data: bytes | None = None
    attempted: bool = False


@dataclass
class Chunk:
    entry: Entry
    coordinates: XZ | None
    allocation: Slice
    header_raw: Slice
    version: int
    header: Header | None = None
    terrain: Frame | None = None
    objects: Frame | None = None
    objects_size: int | None = None
    notes: list[Note] = field(default_factory=list)

    @property
    def physical_size(self) -> int | None:
        if self.header is None:
            return None
        if self.version == 5:
            return 20 + self.header.compressed_size
        if self.objects_size is None:
            return None
        return (24 if self.version == 6 else 32) + self.header.compressed_size + self.objects_size


@dataclass(frozen=True)
class Location:
    path: Path
    region: XZ | None
    index: int
    chunk: XZ | None
