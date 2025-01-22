from scfile.consts import FileSignature
from scfile.core import FileEncoder
from scfile.core.context import ImageContent, ImageOptions
from scfile.enums import FileFormat


class PngEncoder(FileEncoder[ImageContent, ImageOptions]):
    format = FileFormat.PNG
    signature = FileSignature.PNG

    _options = ImageOptions

    def serialize(self):
        self.write(self.data.image)
