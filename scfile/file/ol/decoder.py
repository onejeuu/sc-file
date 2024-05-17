from typing import Any

import lz4.block  # type: ignore
from quicktex import RawTexture  # type: ignore
from quicktex.s3tc.bc3 import BC3Encoder  # type: ignore
from quicktex.s3tc.bc5 import BC5Decoder, BC5Texture  # type: ignore

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.file.data import TextureData
from scfile.file.dds import DdsEncoder
from scfile.io import OlFileIO

from .._base import FileDecoder
from .converter.base import RGBA8Converter
from .converter.bgra8 import BGRA8Converter
from .converter.rgba32f import RGBA32FConverter
from .formats import SUPPORTED_FORMATS


class OlDecoder(FileDecoder[OlFileIO, TextureData]):
    CONVERT_TO_RGBA8 = True
    CONVERT_TO_DXT5 = False

    def to_dds(self):
        return self.convert_to(DdsEncoder)

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
        return TextureData(self.width, self.height, self.linear_size, self.fourcc, self.image)

    def parse(self):
        self._parse_header()
        self._parse_fourcc()
        self._parse_sizes()
        self._parse_image()
        self._convert()

    def _parse_header(self):
        self.width = self.f.readb(F.U32)
        self.height = self.f.readb(F.U32)
        self.mipmap_count = self.f.readb(F.U32)

    def _parse_fourcc(self):
        self.fourcc = self.f.readfourcc()

        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnknownFourcc(self.path, self.fourcc.decode())

    def _read_sizes(self):
        return [self.f.readb(F.U32) for _ in range(self.mipmap_count)]

    def _parse_sizes(self):
        self.uncompressed = self._read_sizes()
        self.compressed = self._read_sizes()

    def _decompress_image(self):
        compressed = self.f.read(self.compressed[0])
        uncompressed_size = self.uncompressed[0]

        self.image = bytes(lz4.block.decompress(compressed, uncompressed_size))  # type: ignore

    def _parse_image(self):
        try:
            self.texture_id = self.f.reads()
            self._decompress_image()

        except Exception:
            raise exc.OlInvalidFormat(self.path)

    def _convert(self):
        if self.CONVERT_TO_RGBA8:
            self._to_rgba8()

        if self.CONVERT_TO_DXT5:
            self._to_dxt5()

    @property
    def linear_size(self) -> int:
        return self.uncompressed[0]

    @property
    def is_compressed(self) -> bool:
        return b"DXT" in self.fourcc

    @property
    def imagedata(self) -> tuple[bytes, int, int]:
        return (self.image, self.width, self.height)

    @property
    def bc5texture(self) -> Any:
        return BC5Texture.from_bytes(*self.imagedata)  # type: ignore

    @property
    def rawtexture(self) -> Any:
        return RawTexture.frombytes(*self.imagedata)  # type: ignore

    def _to_rgba8(self):
        match self.fourcc:
            case b"BGRA8":
                self.image = BGRA8Converter(*self.imagedata).to_rgba8()

            case b"RGBA32F":
                self.image = RGBA32FConverter(*self.imagedata).to_rgba8()

            case b"DXN_XY":
                self.image = bytes(BC5Decoder().decode(self.bc5texture))  # type: ignore
                self.image = RGBA8Converter(*self.imagedata).invert()

            case _:
                pass

    def _to_dxt5(self):
        if not self.is_compressed:
            self.fourcc = b"DXT5"
            self.image = bytes(BC3Encoder(level=9).encode(self.rawtexture))  # type: ignore
