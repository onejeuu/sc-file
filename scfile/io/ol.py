from scfile.consts import CubemapFaces, OlString
from scfile.enums import StructFormat as F

from .streams import StructFileIO


class OlFileIO(StructFileIO):
    def readsizes(self, mipmap_count: int) -> list[int]:
        return [self.readb(F.U32) for _ in range(mipmap_count)]

    def readhdrisizes(self, mipmap_count: int) -> list[list[int]]:
        return [[self.readb(F.U32) for _ in range(mipmap_count)] for _ in range(CubemapFaces.COUNT)]

    def readfourcc(self) -> bytes:
        # Read string and skip last 0x00 byte
        string = self.read(OlString.SIZE)[:-1]

        # Xor byte if it's is not null
        return bytes(byte ^ OlString.XOR for byte in string if byte != OlString.NULL)
