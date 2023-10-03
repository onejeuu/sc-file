import struct
from io import BytesIO

from scfile.consts import DDS, DDSFormat, PixelFormatType, Magic

from .base import BaseOutputFile


class DdsFile(BaseOutputFile):
    def __init__(
        self,
        buffer: BytesIO,
        filename: str,
        width: int,
        height: int,
        image_data: bytes,
        ddsformat: DDSFormat
    ):
        super().__init__(buffer, filename)
        self.width = width
        self.height = height
        self.image_data = image_data
        self.ddsformat = ddsformat

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
        match self.ddsformat.value.type:
            case PixelFormatType.COMPRESSED:
                return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE

            case PixelFormatType.UNCOMPRESSED:
                return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def pitch_or_linear_size(self) -> int:
        match self.ddsformat.value.type:
            case PixelFormatType.COMPRESSED:
                return len(self.image_data)

            case PixelFormatType.UNCOMPRESSED:
                return self.width * 4

    def _add_pixel_format(self) -> None:
        self._write(DDS.PF.SIZE)

        match self.ddsformat.value.type:
            case PixelFormatType.COMPRESSED:
                self._add_compressed_format()

            case PixelFormatType.UNCOMPRESSED:
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
        self._buffer.write(self.ddsformat.value.name)

    def _write(self, i: int) -> None:
        self._buffer.write(struct.pack("<I", i))

    def _space(self, i: int) -> None:
        self._buffer.write(b'\x00' * i * 4)

    def _fill(self) -> None:
        position = self._buffer.tell()
        header_size = DDS.HEADER.SIZE + len(Magic.DDS)
        count = header_size - position
        self._buffer.write(b'\x00' * count)
