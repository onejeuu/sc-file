from typing import List

import lz4.block
from quicktex import RawTexture  # type: ignore
from quicktex.s3tc.bc3 import BC3Encoder  # type: ignore
from quicktex.s3tc.bc5 import BC5Decoder, BC5Texture  # type: ignore

from scfile import exceptions as exc
from scfile.consts import CUBEMAP_FACES, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.files.output.dds import DdsFile, DdsOutputData
from scfile.utils.ol.bgra8 import BGRA8Converter
from scfile.utils.ol.rgba32f import RGBA32FConverter

from .base import BaseSourceFile


SUPPORTED_FORMATS = [
    b"DXT1",
    b"DXT3",
    b"DXT5",
    b"RGBA8",
    b"BGRA8",
    b"RGBA32F",
    b"DXN_XY"
]


class OlFile(BaseSourceFile):

    CONVERT_TO_RGBA8 = True
    CONVERT_TO_DXT5 = True

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
            self.linear_size,
            self.fourcc,
            self.is_cubemap,
            self.imagedata
        )

    def parse(self) -> None:
        # Read header
        # TODO: maybe Texture dataclass?
        self.width = self.r.readbin(F.U32)
        self.height = self.r.readbin(F.U32)
        self.mipmap_count = self.r.readbin(F.U32)

        # Read encrypted FourCC (dds pixel format)
        self.fourcc = self.r.readfourcc()

        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnknownFourcc(self.path, self.fourcc.decode())

        # Read lz4 uncompressed and compressed sizes
        # TODO: all mipmaps decoding
        self._parse_sizes()

        try:
            self.texture_id = self.r.readstring()
            self._decompress_imagedata()

        except Exception:
            raise exc.OlInvalidFormat(self.path)

        if self.CONVERT_TO_RGBA8:
            self._to_rgba8()

        if self.CONVERT_TO_DXT5:
            self._to_dxt5()

    def _to_rgba8(self):
        match self.fourcc:
            case b"BGRA8":
                self.fourcc = b"RGBA8"
                self.imagedata = BGRA8Converter(self.data).to_rgba8()

            case b"RGBA32F":
                self.fourcc = b"RGBA8"
                self.imagedata = RGBA32FConverter(self.data).to_rgba8()

            case b"DXN_XY":
                # TODO: correct colors
                self.fourcc = b"RGBA8"
                self.imagedata = BC5Decoder().decode(self.bc5texture)

    def _to_dxt5(self):
        match self.fourcc:
            case b"RGBA8":
                self.fourcc = b"DXT5"
                self.imagedata = BC3Encoder().encode(self.rawtexture)

    @property
    def linear_size(self) -> int:
        return self.uncompressed[0]

    @property
    def bc5texture(self):
        return BC5Texture.from_bytes(self.imagedata, self.width, self.height)

    @property
    def rawtexture(self):
        return RawTexture.frombytes(self.imagedata, self.width, self.height)

    def _read_sizes(self) -> List[int]:
        return [self.r.readbin(F.U32) for _ in range(self.mipmap_count)]

    def _parse_sizes(self) -> None:
        self.uncompressed = self._read_sizes()
        self.compressed = self._read_sizes()

    def _decompress_imagedata(self) -> None:
        imagedata = lz4.block.decompress(
            self.r.read(self.compressed[0]),
            self.uncompressed[0]
        )

        self.imagedata = bytes(imagedata)


class OlCubemapFile(OlFile):

    is_cubemap = True

    @property
    def linear_size(self) -> int:
        return 0

    def _read_sizes(self) -> List[List[int]]:
        return [
            [self.r.readbin(F.U32) for _ in range(CUBEMAP_FACES)]
            for _ in range(self.mipmap_count)
        ]

    def _parse_sizes(self) -> None:
        self.uncompressed = self._read_sizes()
        self.compressed = self._read_sizes()

    def _decompress_imagedata(self) -> None:
        imagedata = bytearray()

        for cubemap in range(CUBEMAP_FACES):
            imagedata.extend(
                lz4.block.decompress(
                    self.r.read(self.compressed[0][cubemap]),
                    self.uncompressed[0][cubemap]
                )
            )

        self.imagedata = bytes(imagedata)
