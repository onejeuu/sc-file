from typing import List

import lz4.block  # type: ignore

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.files import DdsFile
from scfile.utils.reader import ByteOrder

from io import BytesIO

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
    order = ByteOrder.BIG

    def to_dds(self) -> bytes:
        return self.convert()

    def _output(self) -> DdsFile:
        return DdsFile(
            self.buffer,
            self.filename,
            self.width,
            self.height,
            self.imagedata,
            self.fourcc,
            self.compressed,
            self.mipmap_count
        )

    def _parse(self) -> None:
        self._parse_header()
        self._parse_imagedata()
        self._parse_packed_dxn()

    def _parse_header(self) -> None:
        self._parse_image_size()
        self._parse_fourcc()
        self._parse_sizes()
        self._parse_id_string()

    def _parse_image_size(self) -> None:
        self.width = self.reader.u32()
        self.height = self.reader.u32()
        self.mipmap_count = self.reader.u32()

    def _parse_fourcc(self) -> None:
        self.fourcc = self.reader.olstring()
        self._check_fourcc()
        self.reader.read(1) # delimiter

    def _parse_sizes(self) -> None:
        self.uncompressed_sizes = [self.reader.u32() for _ in range(self.mipmap_count)]
        self.compressed_sizes = [self.reader.u32() for _ in range(self.mipmap_count)]

    def _parse_id_string(self) -> None:
        id_size = self.reader.u16()
        "".join(chr(self.reader.i8()) for _ in range(id_size))

    def _parse_imagedata(self):
        imagedata = BytesIO()

        for index in range(self.mipmap_count):
            imagedata.write(
                lz4.block.decompress(
                    self.reader.read(self.compressed_sizes[index]),
                    self.uncompressed_sizes[index]
                )
            )

        self.imagedata = imagedata.getvalue()

    def _parse_packed_dxn(self):
        if self.fourcc == b"DXN_XY":
            self.imagedata = self._unpack_dxn()
            self.fourcc = b"BGRA8"

    @property
    def compressed(self) -> bool:
        return self.fourcc in (b"DXT1", b"DXT3", b"DXT5")

    def _check_fourcc(self) -> None:
        if self.fourcc not in _SUPPORTED_FORMATS:
            raise exc.OlUnsupportedFormat(f"Unsupported format: {self.fourcc.decode()}")

    def _unpack_dxn(self) -> bytes:
        # its still awesome

        self._validate_dimensions()

        unpacked = bytearray(self.width * self.height * 4)
        position = 0

        for y in range(self.height // 4):
            for x in range(self.width // 4):
                colors = list(self.imagedata[position:position + 8])
                r = self._unpack_square(colors)
                position += 8

                colors = list(self.imagedata[position:position + 8])
                g = self._unpack_square(colors)
                position += 8

                self._copy_unpacked(unpacked, x, y, r, g)

        return bytes(unpacked)

    def _validate_dimensions(self):
        if self.width * self.height != self.uncompressed_sizes[0]:
            raise exc.OlUnpackingError("Invalid buffer length")

        if self.width % 4 != 0 or self.height % 4 != 0:
            raise exc.OlUnpackingError("Dimensions not multiple of 4")

    def _unpack_square(self, colors: List[int]):
        color0, color1, indices = colors[0], colors[1], colors[2:]

        palette = self._create_palette(color0, color1)
        indices = self._calculate_indices(indices)

        square = self._create_empty_square()

        for i in range(4):
            for j in range(4):
                indices, k = divmod(indices, 8)
                square[i][j] = palette[k]

        return square

    def _create_palette(self, color0, color1) -> List[int]:
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

        return palette

    def _calculate_indices(self, indices) -> int:
        return sum((indices[i] << (i * 8)) for i in range(6))

    def _create_empty_square(self) -> List[List[int]]:
        return [[0] * 4 for _ in range(4)]

    def _copy_unpacked(self, unpacked_data, x, y, r, g):
        for ky in range(4):
            for kx in range(4):
                pixel_index = ((y * 4 + ky) * self.width + (x * 4 + kx)) * 4
                unpacked_data[pixel_index:pixel_index + 4] = (
                    0xFF, r[ky][kx], g[ky][kx], 0xFF
                )
