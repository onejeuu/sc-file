from typing import override

from scfile.consts import FormatSignature
from scfile.structures.content import ImageContent
from scfile.core import Decoder
from scfile.enums import ByteOrder, FileFormat


class MicDecoder(Decoder[ImageContent]):
    format = FileFormat.MIC
    signature = FormatSignature.MIC
    order = ByteOrder.LITTLE

    content_type = ImageContent

    @override
    def _parse(self):
        self.data.image = self.io.read()
