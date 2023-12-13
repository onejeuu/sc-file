import lz4.block

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.files.output.dds import DdsFile, DdsOutputData
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

    output = DdsFile
    signature = Signature.OL
    order = ByteOrder.BIG

    is_cubemap = False

    def to_dds(self) -> bytes:
        return self.convert()

    @property
    def data(self) -> DdsOutputData:
        return DdsOutputData(
            self.width,
            self.height,
            self.mipmap_count,
            self.linear_size,
            self.fourcc,
            self.is_cubemap,
            self.imagedata
        )

    def parse(self) -> None:
        # Read header
        self.width = self.reader.u32()
        self.height = self.reader.u32()
        self.mipmap_count = self.reader.u32()

        # Read encrypted FourCC (dds pixel format)
        self.fourcc = self.reader.string_ol_fourcc()

        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnknownFourcc(self.path, self.fourcc.decode())

        # Read lz4 uncompressed and compressed sizes
        self._parse_sizes()

        try:
            self.texture_id = self.reader.string_ol_id()
            self._decompress_imagedata()

        except Exception:
            raise exc.OlInvalidFormat(self.path)

    @property
    def linear_size(self) -> int:
        return self.uncompressed[0]

    def _read_sizes(self) -> list[int]:
        return [self.reader.u32() for _ in range(self.mipmap_count)]

    def _parse_sizes(self) -> None:
        self.uncompressed = self._read_sizes()
        self.compressed = self._read_sizes()

    def _decompress_imagedata(self) -> None:
        imagedata = bytearray()

        for mipmap in range(self.mipmap_count):
            imagedata.extend(
                lz4.block.decompress(
                    self.reader.read(self.compressed[mipmap]),
                    self.uncompressed[mipmap]
                )
            )

        self.imagedata = bytes(imagedata)


class OlCubemapFile(OlFile):

    # +x, -x, +y, -y, +z, -z
    CUBEMAP_DATA_SIZE = 6

    is_cubemap = True

    @property
    def linear_size(self) -> int:
        return 0

    def _read_sizes(self) -> list[list[int]]:
        return [
            [self.reader.u32() for _ in range(self.CUBEMAP_DATA_SIZE)]
            for _ in range(self.mipmap_count)
        ]

    def _parse_sizes(self) -> None:
        self.uncompressed = self._read_sizes()
        self.compressed = self._read_sizes()

    def _decompress_imagedata(self) -> None:
        imagedata = bytearray()

        for mipmap in range(self.mipmap_count):
            for cubemap in range(self.CUBEMAP_DATA_SIZE):
                imagedata.extend(
                    lz4.block.decompress(
                        self.reader.read(self.compressed[mipmap][cubemap]),
                        self.uncompressed[mipmap][cubemap]
                    )
                )

        self.imagedata = bytes(imagedata)
