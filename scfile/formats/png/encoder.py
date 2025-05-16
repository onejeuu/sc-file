from scfile.consts import FileSignature
from scfile.core import FileEncoder
from scfile.core.context import ImageContent
from scfile.enums import FileFormat


class PngEncoder(FileEncoder[ImageContent]):
    format = FileFormat.PNG
    signature = FileSignature.PNG

    def serialize(self):
        self.write(self.data.image)
