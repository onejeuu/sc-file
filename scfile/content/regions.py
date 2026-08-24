"""Data structures for world regions."""

from dataclasses import dataclass, field


_EMPTY_VIEW = memoryview(b"")


@dataclass
class ChunkHeader:
    """Header of compressed world chunk."""

    record_size: int = 0
    section_mask: int = 0
    add_mask: int = 0
    terrain_size: int = 0
    compressed_size: int = 0


@dataclass
class RegionSection:
    y: int = 0
    blocks: memoryview = _EMPTY_VIEW
    metadata: memoryview = _EMPTY_VIEW
    additions: memoryview = _EMPTY_VIEW


@dataclass
class RegionChunk:
    """World terrain chunk."""

    index: int = 0
    header: ChunkHeader = field(default_factory=ChunkHeader)
    payload: bytes = field(default_factory=bytes)

    sections: tuple[RegionSection, ...] = ()
    lighting: memoryview = _EMPTY_VIEW
    biomes: memoryview = _EMPTY_VIEW
    records: memoryview = _EMPTY_VIEW
