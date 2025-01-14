import lz4.block

from scfile.consts import FileSignature
from scfile.core import FileDecoder, TextureContext, TextureOptions
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.formats.dds.encoder import DdsEncoder
from scfile.io.formats.ol import OlFileIO

from .formats import SUPPORTED_FORMATS


class OlDecoder(FileDecoder[TextureContext, OlFileIO, TextureOptions]):
    order = ByteOrder.BIG
    signature = FileSignature.OL

    _opener = OlFileIO
    _context = TextureContext
    _options = TextureOptions

    def to_dds(self):
        return self.convert_to(DdsEncoder)

    def parse(self):
        self.parse_header()
        self.parse_fourcc()
        self.parse_sizes()
        self.parse_image()

    def parse_header(self):
        self.ctx.width = self.f.readb(F.U32)
        self.ctx.height = self.f.readb(F.U32)
        self.ctx.mipmap_count = self.f.readb(F.U32)

    def parse_fourcc(self):
        self.ctx.fourcc = self.f.readfourcc()

        if self.ctx.fourcc not in SUPPORTED_FORMATS:
            raise Exception(self.path, self.ctx.fourcc.decode(encoding="utf-8", errors="replace"))

        # ? change strange naming
        if self.ctx.fourcc == b"DXN_XY":
            self.ctx.fourcc = b"ATI2"

    def parse_sizes(self):
        self.ctx.uncompressed = self.f.readsizes(self.ctx.mipmap_count)
        self.ctx.compressed = self.f.readsizes(self.ctx.mipmap_count)

    def decompress_mipmaps(self):
        for mipmap in range(self.ctx.mipmap_count):
            self.ctx.mipmaps.append(
                lz4.block.decompress(
                    self.f.read(self.ctx.compressed[mipmap]),
                    self.ctx.uncompressed[mipmap],
                )
            )

    def parse_image(self):
        self.texture_id = self.f.reads()
        self.decompress_mipmaps()
