"""
Data structures for world regions.
"""

from dataclasses import dataclass, field


@dataclass
class ChunkHeader:
    """Header of compressed world chunk."""

    full_size: int = 0
    blocks_mask: int = 0
    add_mask: int = 0
    fixed_size: int = 0
    compressed_size: int = 0


@dataclass
class RegionChunk:
    """World chunk."""

    index: int = 0
    header: ChunkHeader = field(default_factory=ChunkHeader)

    blocks: bytes = field(default_factory=bytes)

    meta: bytes = field(default_factory=bytes)
    light: bytes = field(default_factory=bytes)
    add: bytes = field(default_factory=bytes)
    extra: bytes = field(default_factory=bytes)
