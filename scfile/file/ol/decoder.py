from typing import Any

import lz4.block
from quicktex import RawTexture
from quicktex.s3tc.bc3 import BC3Encoder
from quicktex.s3tc.bc5 import BC5Decoder, BC5Texture

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.file.data import TextureData
from scfile.file.dds.encoder import DdsEncoder
from scfile.file.decoder import FileDecoder
from scfile.io.ol import OlFileIO

from .converter.base import RGBA8Converter
from .converter.bgra8 import BGRA8Converter
from .converter.rgba32f import RGBA32FConverter
from .formats import SUPPORTED_FORMATS


class OlDecoder(FileDecoder[OlFileIO, TextureData]):
    CONVERT_TO_RGBA8 = True
    CONVERT_TO_DXT5 = True

    def to_dds(self):
        return self.convert(DdsEncoder)

    @property
    def opener(self):
        return OlFileIO

    @property
    def order(self):
        return ByteOrder.BIG

    @property
    def signature(self):
        return Signature.OL

    def create_data(self):
        return TextureData(
            self.width, self.height, self.linear_size, self.fourcc, self.image
        )

    def parse(self):
        # Read header
        self.width = self.f.readb(F.U32)
        self.height = self.f.readb(F.U32)
        self.mipmap_count = self.f.readb(F.U32)

        # Read encrypted FourCC (dds pixel format)
        self.fourcc = self.f.readfourcc()

        # Validate format
        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnknownFourcc(self.path, self.fourcc.decode())

        # Read lz4 uncompressed and compressed sizes
        self._parse_sizes()

        try:
            self.texture_id = self.f.reads()
            self._decompress_imagedata()

        except Exception:
            raise exc.OlInvalidFormat(self.path)

        if self.CONVERT_TO_RGBA8:
            self._to_rgba8()

        if self.CONVERT_TO_DXT5:
            self._to_dxt5()

    @property
    def linear_size(self) -> int:
        return self.uncompressed[0]

    @property
    def imagedata(self):
        return (self.image, self.width, self.height)

    @property
    def bc5texture(self) -> Any:
        # TODO: Add type hints
        return BC5Texture.from_bytes(*self.imagedata)

    @property
    def rawtexture(self) -> Any:
        # TODO: Add type hints
        return RawTexture.frombytes(*self.imagedata)

    def _to_rgba8(self):
        match self.fourcc:
            case b"BGRA8":
                self.image = BGRA8Converter(*self.imagedata).to_rgba8()

            case b"RGBA32F":
                self.image = RGBA32FConverter(*self.imagedata).to_rgba8()

            case b"DXN_XY":
                # TODO: Validate this
                self.image = bytes(BC5Decoder().decode(self.bc5texture))
                self.image = RGBA8Converter(*self.imagedata).invert()

    def _to_dxt5(self):
        if not self.is_compressed:
            self.fourcc = b"DXT5"
            self.image = bytes(BC3Encoder(level=9).encode(self.rawtexture))

    @property
    def is_compressed(self) -> bool:
        return b"DXT" in self.fourcc

    def _read_sizes(self) -> list[int]:
        return [self.f.readb(F.U32) for _ in range(self.mipmap_count)]

    def _parse_sizes(self) -> None:
        self.uncompressed = self._read_sizes()
        self.compressed = self._read_sizes()

    def _decompress_imagedata(self) -> None:
        # TODO: Decompress all mipmaps

        imagedata = lz4.block.decompress(
            self.f.read(self.compressed[0]), self.uncompressed[0]
        )

        self.image = bytes(imagedata)
