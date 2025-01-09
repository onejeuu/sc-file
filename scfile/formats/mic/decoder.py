from scfile.consts import FileSignature
from scfile.core import FileDecoder, ImageContext, ImageOptions
from scfile.enums import ByteOrder
from scfile.io.file import StructFileIO


class MicDecoder(FileDecoder[StructFileIO, ImageContext, ImageOptions]):
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

    def parse(self):
        self.ctx.image = self.f.read()  # 23 lines of template vs 1 line of action, kinda cool... i guess...
