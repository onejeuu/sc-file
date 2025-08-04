from scfile.consts import FileSignature
from scfile.core import FileDecoder, ImageContent
from scfile.enums import FileFormat


class MicDecoder(FileDecoder[ImageContent]):
    format = FileFormat.MIC
    signature = FileSignature.MIC

    _content = ImageContent

    def to_png(self):
        from scfile.formats.png.encoder import PngEncoder
        return self.convert_to(PngEncoder)

    def parse(self):
        self.data.image = self.read()
