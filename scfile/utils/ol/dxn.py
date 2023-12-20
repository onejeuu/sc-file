from typing import List, Dict

from .converter import Converter


class DxnConverter(Converter):
    def to_rgba(self) -> bytes:
        w, h = self.data.width, self.data.height
        imagedata = bytearray(w * h * 4)
        block_size = 16

        offset = 0

        for y in range(h // 4):
            for x in range(w // 4):
                block = self.data.image[offset:offset + block_size]
                offset += block_size

                channel1 = self.unpack_channel(block[:8]) # red
                channel2 = self.unpack_channel(block[8:]) # green

                for j in range(4):
                    for i in range(4):
                        index = ((y * 4 + j) * w + (x * 4 + i)) * 4
                        imagedata[index:index + 4] = [0xFF, channel1[j][i], channel2[j][i], 0xFF]

        return bytes(imagedata)

    def unpack_channel(self, channel: bytes) -> Dict[int, List[int]]:
        color0, color1, indices = channel[0], channel[1], channel[2:]

        palette = self.create_palette(color0, color1)
        indices = self.calculate_indices(indices)

        unpacked = {}

        for i in range(4):
            unpacked[i] = {}
            for j in range(4):
                k = indices & 0x7
                indices >>= 3
                unpacked[i][j] = palette[k]

        return unpacked

    def create_palette(self, color0: int, color1: int) -> List[int]:
        size = 8
        palette = [0] * size
        palette[:2] = color0, color1

        if color0 < color1:
            size -= 2
            palette[6:] = [0, 0xFF]

        div = size - 1

        for i in range(2, size):
            palette[i] = ((size - i) * color0 + (i - 1) * color1) // div

        return palette

    def calculate_indices(self, indices: bytes) -> int:
        return (
            (indices[0]) |
            (indices[1] << 8) |
            (indices[2] << 16) |
            (indices[3] << 24) |
            (indices[4] << 32) |
            (indices[5] << 40)
        )
