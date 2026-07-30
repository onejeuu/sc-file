from scfile.consts import FileSignature
from scfile.core import FileEncoder, ImageContent
from scfile.enums import ByteOrder, FileFormat


class PngEncoder(FileEncoder[ImageContent]):
    content_type = ImageContent
    format = FileFormat.PNG
    signature = FileSignature.PNG
    order = ByteOrder.LITTLE

    def _serialize(self):
        self.io.write(self.data.image)
