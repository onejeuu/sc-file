import struct
from io import BytesIO

from scfile.consts import DDS, Magic

from .base import BaseOutputFile


class DdsFile(BaseOutputFile):
    def __init__(
        self,
        buffer: BytesIO,
        filename: str,
        width: int,
        height: int,
        image_data: bytes,
        fourcc: bytes,
        compressed: bool
    ):
        super().__init__(buffer, filename)
        self.width = width
        self.height = height
        self.image_data = image_data
        self.fourcc = fourcc
        self.compressed = compressed

    def create(self) -> bytes:
        self._add_magic()
        self._add_header()
        self._add_image_data()

        return self.result

    def _add_magic(self) -> None:
        self._buffer.write(bytes(Magic.DDS))

    def _add_header(self) -> None:
        self._write(DDS.HEADER.SIZE)
        self._write(self.flags)
        self._write(self.height)
        self._write(self.width)
        self._write(self.pitch_or_linear_size)
        self._space(1) # Depth
        self._space(1) # MipMapCount
        self._space(11) # Reserved
        self._add_pixel_format()
        self._write(DDS.TEXTURE)
        self._fill()

    @property
    def flags(self) -> int:
        if self.compressed:
            return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE
        return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def pitch_or_linear_size(self) -> int:
        if self.compressed:
            return len(self.image_data)
        return self.width * 4

    def _add_pixel_format(self) -> None:
        self._write(DDS.PF.SIZE)

        if self.compressed:
            self._add_compressed_format()
        else:
            self._add_uncompressed_format()

    def _add_compressed_format(self) -> None:
        self._write(DDS.PF.FLAG.FOURCC)
        self._add_fourcc()
        self._space(5) # Bitmasks

    def _add_uncompressed_format(self) -> None:
        self._write(DDS.PF.FLAG.RGB | DDS.PF.FLAG.ALPHAPIXELS)
        self._space(1) # FourCC
        self._write(DDS.PF.BIT_COUNT)
        self._write(DDS.PF.BITMASK.R)
        self._write(DDS.PF.BITMASK.G)
        self._write(DDS.PF.BITMASK.B)
        self._write(DDS.PF.BITMASK.A)

    def _add_image_data(self) -> None:
        self._buffer.write(self.image_data)

    def _add_fourcc(self) -> None:
        self._buffer.write(self.fourcc)

    def _write(self, i: int) -> None:
        self._buffer.write(struct.pack("<I", i))

    def _space(self, i: int) -> None:
        self._buffer.write(b'\x00' * i * 4)

    def _fill(self) -> None:
        position = self._buffer.tell()
        header_size = DDS.HEADER.SIZE + len(Magic.DDS)
        count = header_size - position
        self._buffer.write(b'\x00' * count)
