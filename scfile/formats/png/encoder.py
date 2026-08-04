from typing import override

from scfile.consts import FileSignature
from scfile.core import Encoder, ImageContent
from scfile.enums import ByteOrder, FileFormat


class PngEncoder(Encoder[ImageContent]):
    content_type = ImageContent
    format = FileFormat.PNG
    signature = FileSignature.PNG
    order = ByteOrder.LITTLE

    @override
    def _serialize(self):
        self.io.write(self.data.image)
