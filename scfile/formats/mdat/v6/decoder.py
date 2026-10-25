from scfile.content.regions import ChunkHeader
from scfile.enums import F

from ..region import RegionDecoder as BaseRegionDecoder
from .objects import header


class RegionDecoder(BaseRegionDecoder):
    version = 6
    key_size = 16
    header_size = 20
    object_header = staticmethod(header)

    def header(self) -> ChunkHeader:
        length, sections, additions, terrain, compressed = self.io.unpack(f"5{F.I32}")
        return ChunkHeader(length, sections, additions, terrain, compressed)
