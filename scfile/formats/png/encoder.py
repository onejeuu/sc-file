from scfile.consts import FileSignature
from scfile.core import FileEncoder, ImageContext
from scfile.core.options import ImageOptions
from scfile.enums import FileFormat


class PngEncoder(FileEncoder[ImageContext, ImageOptions]):
    format = FileFormat.PNG
    signature = FileSignature.PNG

    _options = ImageOptions

    def serialize(self):
        self.b.write(self.ctx.image)
