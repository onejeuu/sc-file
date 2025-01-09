from scfile.consts import FileSignature
from scfile.core import FileEncoder, ImageContext
from scfile.enums import FileFormat


class PngEncoder(FileEncoder[ImageContext]):
    signature = FileSignature.PNG

    @property
    def format(self):
        return FileFormat.PNG

    def serialize(self):
        self.b.write(self.ctx.image)
