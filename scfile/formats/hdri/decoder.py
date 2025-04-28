import lz4.block

from scfile.consts import CubemapFaces
from scfile.formats.ol.decoder import BaseOlDecoder
from scfile.structures.texture import CubemapTexture


class OlCubemapDecoder(BaseOlDecoder[CubemapTexture]):
    def prepare(self):
        self.data.is_hdri = True
        self.data.texture = CubemapTexture()

    def parse_sizes(self):
        self.data.texture.uncompressed = self.readhdrisizes(self.data.mipmap_count)
        self.data.texture.compressed = self.readhdrisizes(self.data.mipmap_count)

    def decompress_mipmaps(self):
        for mipmap in range(self.data.mipmap_count):
            for face in range(CubemapFaces.COUNT):
                self.data.texture.faces[face].append(
                    lz4.block.decompress(
                        self.read(self.data.compressed[mipmap][face]),  # type: ignore
                        self.data.uncompressed[mipmap][face],  # type: ignore
                    )
                )
