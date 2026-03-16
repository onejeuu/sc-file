from dataclasses import dataclass


@dataclass
class RegionChunk:
    index: int

    sections_mask: int
    add_mask: int

    blocks: bytes
    meta: bytes
    light: bytes
    add: bytes
    extra: bytes
