from scfile.consts import FileSignature
from scfile.core import FileDecoder
from scfile.core.context import ImageContent, ImageOptions
from scfile.enums import FileFormat
from scfile.formats.png.encoder import PngEncoder


class MicDecoder(FileDecoder[ImageContent, ImageOptions]):
    format = FileFormat.MIC
    signature = FileSignature.MIC

    _content = ImageContent
    _options = ImageOptions

    def to_png(self):
        return self.convert_to(PngEncoder)

    def parse(self):
        self.data.image = self.read()
