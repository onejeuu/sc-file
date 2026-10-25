from scfile.content.regions import ChunkHeader
from scfile.enums import F

from ..region import RegionDecoder as BaseRegionDecoder
from .objects import header


class RegionDecoder(BaseRegionDecoder):
    version = 7
    key_size = 8
    header_size = 28
    object_header = staticmethod(header)

    def header(self) -> ChunkHeader:
        length = self.io.value(F.I32)
        key = self.io.read_exact(8)
        sections, additions, terrain, compressed = self.io.unpack(f"4{F.I32}")
        return ChunkHeader(length, sections, additions, terrain, compressed, key)
