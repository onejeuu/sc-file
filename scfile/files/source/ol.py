import lz4.block  # type: ignore

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.files import DdsFile
from scfile.reader import ByteOrder

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
            self.mipmap_count,
            self.linear_size,
            self.fourcc,
            self.imagedata
        )

    def _parse(self) -> None:
        # Read header
        self.width = self.reader.u32()
        self.height = self.reader.u32()
        self.mipmap_count = self.reader.u32()

        # Read encrypted FourCC (dds pixel format)
        self.fourcc = self.reader.ol_fourcc_string()
        self.reader.read(1)

        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnsupportedFormat(self.path, self.fourcc.decode())

        # Read lz4 uncompressed and compressed sizes
        self.uncompressed_sizes = [self.reader.u32() for _ in range(self.mipmap_count)]
        self.compressed_sizes = [self.reader.u32() for _ in range(self.mipmap_count)]

        # TODO: cubemaps - 2 times range mipmap_count, 3 times u16

        # Total number of bytes in main image
        self.linear_size = self.uncompressed_sizes[0]

        # Read id string
        self.id_size = self.reader.u16()
        self.id_str = self.reader.ol_id_string(self.id_size)

        # Decompress image data
        imagedata = bytearray()

        for index in range(self.mipmap_count):
            imagedata.extend(
                lz4.block.decompress(
                    self.reader.read(self.compressed_sizes[index]),
                    self.uncompressed_sizes[index]
                )
            )

        self.imagedata = bytes(imagedata)

    def __repr__(self):
        return (
            f"<OlFile> {self.width}x{self.height} [{self.mipmap_count}] {self.fourcc}\n"
            f"📤 {self.uncompressed_sizes}\n"
            f"📥 {self.compressed_sizes}"
        )
