import lz4.block

from scfile import exceptions, formats
from scfile.consts import CubemapFaces, FileSignature
from scfile.core import FileDecoder, TextureContent
from scfile.core.types import TextureData
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.textures import CubemapTexture, DefaultTexture

from .enums import TextureKind
from .exceptions import OlFormatUnsupported, OlKindUnsupported
from .formats import SUPPORTED_FORMATS
from .io import OlFileIO


class OlDecoder(FileDecoder[TextureContent[TextureData]], OlFileIO):
    format = FileFormat.OL
    signature = FileSignature.OL
    order = ByteOrder.BIG

    _content = TextureContent

    def as_dds(self):
        return self.convert_to(formats.dds.DdsEncoder)

    def parse(self):
        self._parse_header()
        self._parse_format()
        self._parse_kind()
        self._parse_sizes()
        self._parse_image()

    def _parse_header(self):
        self.data.width = self._readb(F.U32)
        self.data.height = self._readb(F.U32)
        self.data.mipmap_count = self._readb(F.U32)

    def _parse_format(self):
        self.data.format = self._readformat()

        if self.data.format not in SUPPORTED_FORMATS:
            raise OlFormatUnsupported(self.location, self.data.format)

    def _parse_kind(self):
        kind = self._readb(F.U8)

        match kind:
            case TextureKind.DEFAULT:
                self.data.texture = DefaultTexture()

            case TextureKind.CUBEMAP:
                self.data.texture = CubemapTexture()

            case _:
                raise OlKindUnsupported(self.location, kind)

    def _parse_sizes(self):
        match self.data.texture:
            case DefaultTexture() as texture:
                texture.uncompressed = self._readsizes(self.data.mipmap_count)
                texture.compressed = self._readsizes(self.data.mipmap_count)

            case CubemapTexture() as texture:
                texture.uncompressed = self._readsizescubemap(self.data.mipmap_count)
                texture.compressed = self._readsizescubemap(self.data.mipmap_count)

    def _parse_image(self):
        self.data.path_hash = self._reads()

        match self.data.texture:
            case DefaultTexture() as texture:
                for mipmap in range(self.data.mipmap_count):
                    texture.mipmaps.append(
                        self._parse_mipmap(
                            texture.compressed[mipmap],
                            texture.uncompressed[mipmap],
                        )
                    )

            case CubemapTexture() as texture:
                for mipmap in range(self.data.mipmap_count):
                    for face in range(CubemapFaces.COUNT):
                        texture.faces[face].append(
                            self._parse_mipmap(
                                texture.compressed[mipmap][face],
                                texture.uncompressed[mipmap][face],
                            )
                        )

    def _parse_mipmap(self, compressed: int, uncompressed: int) -> bytes:
        position = self.tell()

        try:
            return lz4.block.decompress(self.read(compressed), uncompressed)

        except lz4.block.LZ4BlockError:
            raise exceptions.InvalidStructureError(self.location, position=position) from None
