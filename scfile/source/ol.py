from typing import Any, List

import lz4.block  # type: ignore

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.output import DdsFile
from scfile.utils.reader import ByteOrder

from .base import BaseSourceFile


_SUPPORTED_FORMATS = [
    b"DXT1",
    b"DXT3",
    b"DXT5",
    b"RGBA8",
    b"BGRA8",
    b"RGBA32F",
    b"DXN_XY"
]


class OlFile(BaseSourceFile):

    signature = Signature.OL

    def to_dds(self) -> bytes:
        return self.convert()

    def _default_output(self) -> None:
        DdsFile(
            self.buffer,
            self.filename,
            self.width,
            self.height,
            self.image_data,
            self.fourcc,
            self.compressed
        ).create()

    def _parse(self) -> None:
        self.reader.order = ByteOrder.BIG

        # reading header
        self.width = self.reader.u32()
        self.height = self.reader.u32()
        streams_count = self.reader.u32()

        # dds pixel format
        self.fourcc = self.reader.olstring()
        self._check_fourcc()

        # delimiter
        self.reader.read(1)

        # reading data sizes, keep first one
        uncompressed_size = [self.reader.u32() for _ in range(streams_count)][0]
        compressed_size = [self.reader.u32() for _ in range(streams_count)][0]

        # skipping id string
        id_size = self.reader.u16()
        "".join(chr(self.reader.i8()) for _ in range(id_size))

        # reading uncompressed pixel data
        self.image_data: bytes = lz4.block.decompress(
            self.reader.read(compressed_size),
            uncompressed_size
        )

        if self.fourcc == b"DXN_XY":
            self.image_data = self._unpack_dxn()
            self.fourcc = b"RGBA8"

    @property
    def compressed(self) -> bool:
        return self.fourcc in (b"DXT1", b"DXT3", b"DXT5")

    def _check_fourcc(self) -> None:
        if self.fourcc not in _SUPPORTED_FORMATS:
            raise exc.OlUnsupportedFormat(f"Unsupported format: {self.fourcc.decode()}")

    def _unpack_dxn(self) -> bytes:
        # TODO: refactor this someone pls idk how

        if self.width * self.height != len(self.image_data):
            raise exc.OlUnpackingError("Invalid buffer length")

        if self.width % 4 != 0 or self.height % 4 != 0:
            raise exc.OlUnpackingError("Dimensions not multiple of 4")

        unpacked = bytearray(self.width * self.height * 4)
        position = 0

        for y in range(self.height // 4):
            for x in range(self.width // 4):
                square_g = self._unpack_square(*self.image_data[position:position+8])
                position += 8

                square_r = self._unpack_square(*self.image_data[position:position+8])
                position += 8

                for ky in range(4):
                    for kx in range(4):
                        pixel_index = ((y * 4 + ky) * self.width + (x * 4 + kx)) * 4
                        unpacked[pixel_index:pixel_index + 4] = (
                            0xFF, square_r[ky][kx], square_g[ky][kx], 0xFF
                        )

        return bytes(unpacked)

    def _unpack_square(self, color0: int, color1: int, indices: Any) -> List[List[int]]:
        # no clue tf is going

        palette = [0] * 8
        palette[:2] = color0, color1

        if color0 > color1:
            palette[2:] = [
                ((8 - i) * color0 + (i - 1) * color1) // 7 for i in range(2, 8)
            ]
        else:
            palette[2:6] = [
                ((6 - i) * color0 + (i - 1) * color1) // 5 for i in range(2, 6)
            ]
            palette[6:] = [0, 0xFF]

        indices = sum((indices[i] << (i * 8)) for i in range(6))

        unpacked_square = [[0] * 4 for _ in range(4)]

        for i in range(4):
            for j in range(4):
                indices, k = divmod(indices, 8)
                unpacked_square[i][j] = palette[k]

        return unpacked_square
