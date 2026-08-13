from typing import override

from scfile.consts import FormatSignature
from scfile.core import Encoder
from scfile.enums import ByteOrder, FileFormat
from scfile.structures.content import ImageContent


class PngEncoder(Encoder[ImageContent]):
    format = FileFormat.PNG
    signature = FormatSignature.PNG
    order = ByteOrder.LITTLE

    content_type = ImageContent

    @override
    def _serialize(self):
        self.io.write(self.data.image)
