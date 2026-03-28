from dataclasses import dataclass


@dataclass
class ChunkHeader:
    full_size: int
    blocks_mask: int
    add_mask: int
    fixed_size: int
    compressed_size: int


@dataclass
class RegionChunk:
    index: int

    header: ChunkHeader

    blocks: bytes
    meta: bytes
    light: bytes
    add: bytes
    extra: bytes
