import struct
from io import BytesIO

from scfile.base import BaseOutputFile
from scfile.consts import DDS, DDSFormat, Magic


class DDSFile(BaseOutputFile):
    def __init__(self, buffer: BytesIO, width: int, height: int, decoded_streams: bytes, ddsformat: DDSFormat):
        super().__init__(buffer)

        self.width = width
        self.height = height
        self.decoded_streams = decoded_streams
        self.ddsformat = ddsformat

    def create(self) -> bytes:
        self._fill_header()
        self.buffer.write(self.decoded_streams)
        return self.output

    def _fill_header(self) -> None:
        self.buffer.write(bytes(Magic.DDS))
        self._write(DDS.HEADER_SIZE)
        self._write(DDS.CAPS | DDS.PIXELFORMAT | DDS.WIDTH | DDS.HEIGHT | DDS.LINEARSIZE)
        self._write(self.width)
        self._write(self.height)
        self._write(len(self.decoded_streams))
        self._space(52)
        self._write(DDS.BIT_COUNT)

        self._match_format()

        self._write(DDS.BLOCK_SIZE)

    def _match_format(self) -> None:
        match self.ddsformat:
            case DDSFormat.DXT1 | DDSFormat.DXT5: self._dxt()
            case DDSFormat.RGBA | DDSFormat.BIT8: self._rgba()

    def _dxt(self) -> None:
        self._write(DDS.FOURCC)
        self.buffer.write(self.ddsformat.value)
        self._space(20)

    def _rgba(self) -> None:
        self._write(DDS.RGB | DDS.ALPHAPIXELS)
        self._space(4)
        self._write(DDS.BIT_COUNT)
        self._write(DDS.R_BITMASK)
        self._write(DDS.G_BITMASK)
        self._write(DDS.G_BITMASK)
        self._write(DDS.A_BITMASK)

    def _write(self, i: int) -> None:
        self.buffer.write(struct.pack("<I", i))

    def _space(self, i: int) -> None:
        self.buffer.write(b'\x00' * i)
