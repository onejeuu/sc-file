"""
Extensions for OL file format with custom struct-based I/O methods.
"""

from scfile.consts import CubemapFaces
from scfile.core import StructIO
from scfile.enums import F


XOR = ord("g")
NULL = ord("G")


class OlFileIO(StructIO):
    def _readsizes(self, mipmap_count: int) -> list[int]:
        return [self._readb(F.U32) for _ in range(mipmap_count)]

    def _readsizescubemap(self, mipmap_count: int) -> list[list[int]]:
        return [[self._readb(F.U32) for _ in range(CubemapFaces.COUNT)] for _ in range(mipmap_count)]

    def _readformat(self) -> bytes:
        # Read string and skip last 0x00 byte
        string = self.read(17)[:-1]

        # Xor fourcc string
        return bytes(byte ^ XOR for byte in string if byte != NULL)
