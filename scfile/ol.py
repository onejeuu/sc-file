from typing import Any, List

import lz4.block # type: ignore

from scfile import exceptions as exc
from scfile.base import BaseInputFile
from scfile.consts import DDSFormat, Signature
from scfile.dds import DDSFile


class OlFile(BaseInputFile):
    @property
    def signature(self) -> int:
        return Signature.OL

    def to_dds(self) -> bytes:
        self._convert()

        DDSFile(
            self.buffer,
            self.width,
            self.height,
            self.decoded_streams,
            self.ddsformat
        ).create()

        return self.output

    def _convert(self) -> bytes:
        # reading header
        self.width = self.reader.udword()
        self.height = self.reader.udword()
        streams_count = self.reader.udword()

        # compression format definition
        olformat = self.reader.zstring()
        self.ddsformat = self.identify_format(olformat)

        # reading data sizes, keep first one
        uncompressed_size = [self.reader.udword() for _ in range(streams_count)][0]
        compressed_size = [self.reader.udword() for _ in range(streams_count)][0]

        # skipping id string
        id_size = self.reader.uword()
        "".join(chr(self.reader.byte()) for _ in range(id_size))

        # reading uncompressed pixel data
        self.decoded_streams: bytes = lz4.block.decompress( # type: ignore
            self.reader.read(compressed_size),
            uncompressed_size
        )

        # unpacking 8bit
        if self.ddsformat == DDSFormat.BIT8:
            self.decoded_streams = self._unpack_bit8()

        return self.output

    def identify_format(self, olformat: str) -> DDSFormat:
        match olformat:
            case "#?3VGGGGGGGGGGGG": return DDSFormat.DXT1
            case "#?3RGGGGGGGGGGGG": return DDSFormat.DXT5
            case "% 5&_GGGGGGGGGGG": return DDSFormat.RGBA
            case "#?)8?>GGGGGGGGGG": return DDSFormat.BIT8
            case _: raise exc.UnknownFormat()

    def _unpack_bit8(self) -> bytes:
        # TODO: refactor this someone pls idk how

        if self.width * self.height != len(self.decoded_streams):
            raise exc.UnpackingError("Invalid buffer length")

        if self.width % 4 != 0 or self.height % 4 != 0:
            raise exc.UnpackingError("Dimensions not multiple of 4")

        unpacked = bytearray(self.width * self.height * 4)
        position = 0

        for y in range(self.height // 4):
            for x in range(self.width // 4):
                square_g = self._unpack_square(*self.decoded_streams[position:position+8])
                position += 8

                square_r = self._unpack_square(*self.decoded_streams[position:position+8])
                position += 8

                for ky in range(4):
                    for kx in range(4):
                        pixel_index = ((y * 4 + ky) * self.width + (x * 4 + kx)) * 4
                        unpacked[pixel_index:pixel_index + 4] = (0xFF, square_r[ky][kx], square_g[ky][kx], 0xFF)

        return bytes(unpacked)

    def _unpack_square(self, color0: int, color1: int, indices: Any) -> List[List[int]]:
        # no clue tf is going

        palette = [0] * 8
        palette[:2] = color0, color1

        if color0 > color1:
            palette[2:] = [((8 - i) * color0 + (i - 1) * color1) // 7 for i in range(2, 8)]
        else:
            palette[2:6] = [((6 - i) * color0 + (i - 1) * color1) // 5 for i in range(2, 6)]
            palette[6:] = [0, 0xFF]

        indices = sum((indices[i] << (i * 8)) for i in range(6))

        unpacked_square = [[0] * 4 for _ in range(4)]

        for i in range(4):
            for j in range(4):
                indices, k = divmod(indices, 8)
                unpacked_square[i][j] = palette[k]

        return unpacked_square
