from typing import override

from scfile.consts import FormatSignature
from scfile.content import ImageContent
from scfile.core import Encoder
from scfile.enums import ByteOrder, FileFormat


class PngEncoder(Encoder[ImageContent]):
    format = FileFormat.PNG
    signature = FormatSignature.PNG
    order = ByteOrder.LITTLE

    content_type = ImageContent

    @override
    def _serialize(self):
        self.io.write(self.data.image)
