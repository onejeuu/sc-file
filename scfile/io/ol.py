from scfile.consts import OlString
from scfile.enums import StructFormat as F

from .binary import BinaryFileIO


class OlFileIO(BinaryFileIO):
    def readsizes(self, mipmap_count: int) -> list[int]:
        """Read lz4 uncompressed or compressed sizes."""
        return [self.readb(F.U32) for _ in range(mipmap_count)]

    def readfourcc(self) -> bytes:
        """Read xor encoded FourCC."""
        # Read string and skip last 0x00 byte
        string = self.read(OlString.SIZE)[:-1]

        # Xor byte if it's is not null
        return bytes(byte ^ OlString.XOR for byte in string if byte != OlString.NULL)
