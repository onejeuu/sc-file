import lz4.block

from scfile import exceptions as exc
from scfile.consts import Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.file.base import FileDecoder
from scfile.file.data import TextureData
from scfile.file.formats.dds import DdsEncoder
from scfile.io import OlFileIO

from .formats import SUPPORTED_FORMATS


class OlDecoder(FileDecoder[OlFileIO, TextureData]):
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
        return TextureData(
            self.width, self.height, self.mipmap_count, self.linear_size, self.fourcc, self.image
        )

    def parse(self):
        self._parse_header()
        self._parse_fourcc()
        self._parse_sizes()
        self._parse_image()

    def _parse_header(self):
        self.width = self.f.readb(F.U32)
        self.height = self.f.readb(F.U32)
        self.mipmap_count = self.f.readb(F.U32)

    def _parse_fourcc(self):
        self.fourcc = self.f.readfourcc()

        if self.fourcc not in SUPPORTED_FORMATS:
            raise exc.OlUnknownFourcc(self.path, self.fourcc.decode())

        self.fourcc = b"ATI2" if self.fourcc == b"DXN_XY" else self.fourcc

    def _parse_sizes(self):
        self.uncompressed = self.f.readsizes(self.mipmap_count)
        self.compressed = self.f.readsizes(self.mipmap_count)

    def _decompress_mipmaps(self):
        self.mipmaps: list[bytes] = []

        for mipmap in range(self.mipmap_count):
            self.mipmaps.append(
                lz4.block.decompress(
                    self.f.read(self.compressed[mipmap]), self.uncompressed[mipmap]
                )
            )

    def _parse_image(self):
        self.texture_id = self.f.reads()

        self._decompress_mipmaps()

        self.image = b"".join(self.mipmaps)

    @property
    def linear_size(self) -> int:
        return self.uncompressed[0]
