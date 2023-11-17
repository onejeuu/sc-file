import struct
from io import BytesIO

from scfile.consts import Magic
from scfile.reader import ByteOrder
from scfile.utils.dds_structure import DDS

from .base import BaseOutputFile


class DdsFile(BaseOutputFile):
    def __init__(
        self,
        buffer: BytesIO,
        filename: str,
        width: int,
        height: int,
        mipmap_count: int,
        linear_size: int,
        fourcc: bytes,
        imagedata: bytes,
    ):
        super().__init__(buffer, filename)
        self.width = width
        self.height = height
        self.mipmap_count = mipmap_count
        self.linear_size = linear_size
        self.fourcc = fourcc
        self.imagedata = imagedata

    def _create(self) -> None:
        self._add_magic()
        self._add_header()
        self._add_imagedata()

    def _add_header(self) -> None:
        self._write(DDS.HEADER.SIZE)
        self._write(self.flags)
        self._write(self.height)
        self._write(self.width)
        self._write(self.pitch_or_linear_size)
        self._space(1) # Depth
        self._write(self.mipmap_count)
        self._space(11) # Reserved
        self._add_pixel_format()
        self._write(DDS.TEXTURE | DDS.MIPMAP | DDS.COMPLEX)
        self._fill()

    @property
    def compressed(self) -> bool:
        return b"DXT" in self.fourcc

    @property
    def flags(self) -> int:
        if self.compressed:
            return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE
        return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def pitch(self):
        aligned_width = (self.width + 3) & ~3
        return aligned_width * DDS.PF.BIT_COUNT

    @property
    def pitch_or_linear_size(self) -> int:
        if self.compressed:
            return self.linear_size
        return self.pitch

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
        self._write(DDS.PF.RGB_FLAGS)
        self._space(1) # FourCC
        self._write(DDS.PF.BIT_COUNT)

        for mask in self._bitmasks:
            self._write(mask, ByteOrder.BIG)

    @property
    def _bitmasks(self):
        match self.fourcc:
            case b"BGRA8":
                return (
                    DDS.PF.BITMASK.A,
                    DDS.PF.BITMASK.B,
                    DDS.PF.BITMASK.G,
                    DDS.PF.BITMASK.R,
                )
            case _:
                return (
                    DDS.PF.BITMASK.A,
                    DDS.PF.BITMASK.R,
                    DDS.PF.BITMASK.G,
                    DDS.PF.BITMASK.B,
                )

    def _add_magic(self) -> None:
        self.buffer.write(bytes(Magic.DDS))

    def _add_fourcc(self) -> None:
        self.buffer.write(self.fourcc)

    def _add_imagedata(self) -> None:
        self.buffer.write(self.imagedata)

    def _write(self, i: int, order: ByteOrder = ByteOrder.LITTLE) -> None:
        self.buffer.write(struct.pack(f"{order}I", i))

    def _space(self, i: int) -> None:
        self.buffer.write(b'\x00' * 4 * i)

    def _fill(self) -> None:
        position = self.buffer.tell()
        header_size = DDS.HEADER.SIZE + len(Magic.DDS)
        count = header_size - position
        self.buffer.write(b'\x00' * count)
