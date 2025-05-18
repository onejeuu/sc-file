from abc import ABC, abstractmethod
from typing import Generic

import lz4.block

from scfile.consts import FileSignature
from scfile.core import FileDecoder
from scfile.core.context import TextureContent
from scfile.core.context.content import TextureType
from scfile.enums import ByteOrder, FileFormat
from scfile.enums import StructFormat as F
from scfile.formats.dds.encoder import DdsEncoder
from scfile.structures.texture import DefaultTexture

from .exceptions import OlUnsupportedFourcc
from .formats import SUPPORTED_FORMATS
from .io import OlFileIO


# mro nightmare
class BaseOlDecoder(FileDecoder[TextureContent[TextureType]], OlFileIO, Generic[TextureType], ABC):
    format = FileFormat.OL
    order = ByteOrder.BIG
    signature = FileSignature.OL

    def to_dds(self):
        return self.convert_to(DdsEncoder)

    def parse(self):
        self.parse_header()
        self.parse_fourcc()
        self.parse_sizes()
        self.parse_image()

    def parse_header(self):
        self.data.width = self.readb(F.U32)
        self.data.height = self.readb(F.U32)
        self.data.mipmap_count = self.readb(F.U32)

    def parse_fourcc(self):
        self.data.fourcc = self.readfourcc()

        if self.data.fourcc not in SUPPORTED_FORMATS:
            raise OlUnsupportedFourcc(self.path, self.data.fourcc)

        if self.data.fourcc == b"DXN_XY":
            self.data.fourcc = b"ATI2"

    def parse_image(self):
        self.texture_id = self.reads()
        self.parse_mipmaps()

    @abstractmethod
    def parse_sizes(self):
        pass

    @abstractmethod
    def parse_mipmaps(self):
        pass


class OlDecoder(BaseOlDecoder[DefaultTexture]):
    _content = TextureContent

    def parse_sizes(self):
        self.data.texture.uncompressed = self.readsizes(self.data.mipmap_count)
        self.data.texture.compressed = self.readsizes(self.data.mipmap_count)

    def parse_mipmaps(self):
        for mipmap in range(self.data.mipmap_count):
            self.data.texture.mipmaps.append(
                lz4.block.decompress(
                    self.read(self.data.texture.compressed[mipmap]),
                    self.data.texture.uncompressed[mipmap],
                )
            )
