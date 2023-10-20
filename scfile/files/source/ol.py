import lz4.block  # type: ignore

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.files import DdsFile
from scfile.reader import ByteOrder
import struct

from io import BytesIO

from .base import BaseSourceFile


SUPPORTED_FORMATS = [
    b"DXT1",
    b"DXT3",
    b"DXT5",
    b"RGBA8",
    b"BGRA8",
    b"RGBA32F",
    #b"DXN_XY"
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
            self.mipmap_count
        )

    def _parse(self) -> None:
        self._parse_header()
        self._parse_imagedata()

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

        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnsupportedFormat(self.fourcc.decode())

        self.reader.read(1) # delimiter

    def _parse_sizes(self) -> None:
        self.uncompressed_sizes = [self.reader.u32() for _ in range(self.mipmap_count)]
        self.compressed_sizes = [self.reader.u32() for _ in range(self.mipmap_count)]

    def _parse_id_string(self) -> None:
        id_size = self.reader.u16()
        "".join(chr(self.reader.i8()) for _ in range(id_size))

    def _parse_imagedata(self) -> None:
        imagedata = BytesIO()

        for index in range(self.mipmap_count):
            imagedata.write(
                lz4.block.decompress(
                    self.reader.read(self.compressed_sizes[index]),
                    self.uncompressed_sizes[index]
                )
            )

        self.imagedata = imagedata.getvalue()
