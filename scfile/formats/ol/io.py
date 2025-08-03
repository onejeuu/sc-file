"""
Extensions for OL file format with custom struct-based I/O methods.
"""

from scfile.consts import CubemapFaces, OlString
from scfile.core.io import StructFileIO
from scfile.enums import F


class OlFileIO(StructFileIO):
    def _readsizes(self, mipmap_count: int) -> list[int]:
        return [self._readb(F.U32) for _ in range(mipmap_count)]

    def _readsizescubemap(self, mipmap_count: int) -> list[list[int]]:
        return [[self._readb(F.U32) for _ in range(CubemapFaces.COUNT)] for _ in range(mipmap_count)]

    def _readformat(self) -> bytes:
        # Read string and skip last 0x00 byte
        string = self.read(OlString.SIZE)[:-1]

        # Xor byte if it's is not null
        return bytes(byte ^ OlString.XOR for byte in string if byte != OlString.NULL)
