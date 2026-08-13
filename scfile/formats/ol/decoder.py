from typing import override

import lz4.block

from scfile import exceptions
from scfile.consts import FormatSignature
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.exceptions import TextureFormatError, TextureKindError
from scfile.io.ol import OlReader
from scfile.structures.content import TextureContent
from scfile.structures.textures import CUBEMAP_FACE_COUNT, CubemapTexture, DefaultTexture

from .enums import TextureKind
from .formats import SUPPORTED_FORMATS


class OlDecoder(Decoder[TextureContent, OlReader]):
    format = FileFormat.OL
    signature = FormatSignature.OL
    order = ByteOrder.BIG

    content_type = TextureContent
    io_factory = OlReader

    @override
    def _parse(self):
        self._parse_header()
        self._parse_format()
        self._parse_kind()
        self._parse_sizes()
        self._parse_image()

    def _parse_header(self):
        self.data.width = self.io.value(F.U32)
        self.data.height = self.io.value(F.U32)
        self.data.mipmap_count = self.io.value(F.U32)

    def _parse_format(self):
        self.data.format = self.io.format()

        if self.data.format not in SUPPORTED_FORMATS:
            raise TextureFormatError(
                self.data.format,
                location=self.location,
                offset=self.io.tell(),
            )

    def _parse_kind(self):
        kind = self.io.value(F.U8)

        match kind:
            case TextureKind.DEFAULT:
                self.data.texture = DefaultTexture()

            case TextureKind.CUBEMAP:
                self.data.texture = CubemapTexture()

            case _:
                raise TextureKindError(
                    kind,
                    location=self.location,
                    offset=self.io.tell(),
                )

    def _parse_sizes(self):
        match self.data.texture:
            case DefaultTexture() as texture:
                texture.uncompressed = self.io.sizes(self.data.mipmap_count)
                texture.compressed = self.io.sizes(self.data.mipmap_count)

            case CubemapTexture() as texture:
                texture.uncompressed = self.io.cubemap_sizes(self.data.mipmap_count)
                texture.compressed = self.io.cubemap_sizes(self.data.mipmap_count)

    def _parse_image(self):
        self.data.path_hash = self.io.prefixed()

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
                    for face in range(CUBEMAP_FACE_COUNT):
                        texture.faces[face].append(
                            self._parse_mipmap(
                                texture.compressed[mipmap][face],
                                texture.uncompressed[mipmap][face],
                            )
                        )

    def _parse_mipmap(self, compressed: int, uncompressed: int) -> bytes:
        position = self.io.tell()

        try:
            return lz4.block.decompress(
                self.io.read_exact(compressed),
                uncompressed,
            )

        except lz4.block.LZ4BlockError:
            raise exceptions.BinaryStructureError(
                location=self.location,
                offset=position,
            ) from None
