import lz4.block

from scfile.consts import CubemapFaces
from scfile.core.context import TextureContent
from scfile.formats.ol.decoder import BaseOlDecoder
from scfile.structures.texture import CubemapTexture


class OlCubemapDecoder(BaseOlDecoder[CubemapTexture]):
    _content = TextureContent

    def prepare(self):
        self.data.texture = CubemapTexture()

    def parse_sizes(self):
        self.data.texture.uncompressed = self.readsizescubemap(self.data.mipmap_count)
        self.data.texture.compressed = self.readsizescubemap(self.data.mipmap_count)

    def parse_mipmaps(self):
        for mipmap in range(self.data.mipmap_count):
            for face in range(CubemapFaces.COUNT):
                self.data.texture.faces[face].append(
                    lz4.block.decompress(
                        self.read(self.data.texture.compressed[mipmap][face]),
                        self.data.texture.uncompressed[mipmap][face],
                    )
                )
