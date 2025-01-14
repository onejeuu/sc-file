from scfile.consts import FileSignature
from scfile.core import FileDecoder, ImageContext, ImageOptions
from scfile.enums import ByteOrder
from scfile.formats.png.encoder import PngEncoder
from scfile.io.streams import StructFileIO


class MicDecoder(FileDecoder[ImageContext, StructFileIO, ImageOptions]):
    order = ByteOrder.LITTLE
    signature = FileSignature.MIC

    @property
    def _opener(self):
        return StructFileIO

    @property
    def _context(self):
        return ImageContext

    @property
    def _options(self):
        return ImageOptions

    def to_png(self):
        return self.convert_to(PngEncoder)

    def parse(self):
        self.ctx.image = self.f.read()
