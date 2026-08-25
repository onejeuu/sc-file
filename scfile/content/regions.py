"""World region structures."""

from dataclasses import dataclass, field


@dataclass
class ChunkHeader:
    """Header of compressed world chunk."""

    record_size: int = 0
    section_mask: int = 0
    add_mask: int = 0
    terrain_size: int = 0
    compressed_size: int = 0


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
