from dataclasses import dataclass


@dataclass
class RegionChunk:
    index: int
    data: bytes
