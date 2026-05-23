"""
Data structures for world regions.
"""

from dataclasses import dataclass


@dataclass
class ChunkHeader:
    """Header of compressed world chunk."""

    full_size: int
    blocks_mask: int
    add_mask: int
    fixed_size: int
    compressed_size: int


@dataclass
class RegionChunk:
    """World chunk."""

    index: int
    header: ChunkHeader
    blocks: bytes
