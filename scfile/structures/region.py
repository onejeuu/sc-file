from dataclasses import dataclass


@dataclass
class RegionChunk:
    index: int
    h1: int
    h2: int
    data: bytes
