from scfile.content.regions import ChunkHeader
from scfile.enums import F

from ..region import RegionDecoder as BaseRegionDecoder


class RegionDecoder(BaseRegionDecoder):
    version = 5
    key_size = 16
    header_size = 20

    def header(self) -> ChunkHeader:
        length, sections, additions, terrain, compressed = self.io.unpack(f"5{F.I32}")
        return ChunkHeader(length, sections, additions, terrain, compressed)
