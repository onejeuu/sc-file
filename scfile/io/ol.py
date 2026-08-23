from scfile.content.textures import CUBEMAP_FACE_COUNT
from scfile.enums import F

from .base import StructReader


XOR = ord("g")
NULL = ord("G")


class OlReader(StructReader):
    def sizes(
        self,
        mipmap_count: int,
    ) -> list[int]:
        # Read mipmap sizes
        return self.array(F.U32, mipmap_count).tolist()

    def cubemap_sizes(
        self,
        mipmap_count: int,
    ) -> list[list[int]]:
        # Read mipmap sizes for each cubemap face
        data = self.array(F.U32, mipmap_count * CUBEMAP_FACE_COUNT)

        # Reshape to mipmap[face]
        return data.reshape(mipmap_count, CUBEMAP_FACE_COUNT).tolist()

    def format(
        self,
    ) -> bytes:
        # Read obfuscated format identifier
        data = self.read_exact(16)

        # Decode format and remove padding
        return bytes(byte ^ XOR for byte in data if byte != NULL)
