from scfile.consts import FileSignature
from scfile.core import FileEncoder, ImageContent
from scfile.enums import ByteOrder, FileFormat


class PngEncoder(FileEncoder[ImageContent]):
    format = FileFormat.PNG
    signature = FileSignature.PNG
    order = ByteOrder.LITTLE

    def serialize(self):
        self.write(self.data.image)
