from abc import ABC, abstractmethod
from typing import Generic

import lz4.block

from scfile.consts import FileSignature
from scfile.core import FileDecoder, TextureContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.texture import DefaultTexture, TextureType

from .exceptions import OlFormatUnsupported
from .formats import SUPPORTED_FORMATS
from .io import OlFileIO


# mro nightmare
class BaseOlDecoder(FileDecoder[TextureContent[TextureType]], OlFileIO, Generic[TextureType], ABC):
    format = FileFormat.OL
    order = ByteOrder.BIG
    signature = FileSignature.OL

    def to_dds(self):
        from scfile.formats.dds.encoder import DdsEncoder
        return self.convert_to(DdsEncoder)

    def parse(self):
        self._parse_header()
        self._parse_format()
        self._parse_sizes()
        self._parse_image()

    def _parse_header(self):
        self.data.width = self._readb(F.U32)
        self.data.height = self._readb(F.U32)
        self.data.mipmap_count = self._readb(F.U32)

    def _parse_format(self):
        self.data.format = self._readformat()

        if self.data.format not in SUPPORTED_FORMATS:
            raise OlFormatUnsupported(self.path, self.data.format)

    def _parse_image(self):
        self.texture_id = self._reads()
        self._parse_mipmaps()

    @abstractmethod
    def _parse_sizes(self):
        pass

    @abstractmethod
    def _parse_mipmaps(self):
        pass


class OlDecoder(BaseOlDecoder[DefaultTexture]):
    _content = TextureContent

    def _parse_sizes(self):
        self.data.texture.uncompressed = self._readsizes(self.data.mipmap_count)
        self.data.texture.compressed = self._readsizes(self.data.mipmap_count)

    def _parse_mipmaps(self):
        for mipmap in range(self.data.mipmap_count):
            self.data.texture.mipmaps.append(
                lz4.block.decompress(
                    self.read(self.data.texture.compressed[mipmap]),
                    self.data.texture.uncompressed[mipmap],
                )
            )
