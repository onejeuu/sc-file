"""
Extensions for OL file format with custom struct-based I/O methods.
"""

from scfile.consts import CubemapFaces
from scfile.enums import F

from .base import StructReader


XOR = ord("g")
NULL = ord("G")


class OlReader(StructReader):
    def sizes(
        self,
        mipmap_count: int,
    ) -> list[int]:
        return [self.value(F.U32) for _ in range(mipmap_count)]

    def cubemap_sizes(
        self,
        mipmap_count: int,
    ) -> list[list[int]]:
        return [[self.value(F.U32) for _ in range(CubemapFaces.COUNT)] for _ in range(mipmap_count)]

    def format(self) -> bytes:
        string = self.read(16)
        return bytes(byte ^ XOR for byte in string if byte != NULL)
