from typing import override

from scfile.consts import FormatSignature
from scfile.content import ImageContent
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat


class MicDecoder(Decoder[ImageContent]):
    format = FileFormat.MIC
    signature = FormatSignature.MIC
    order = ByteOrder.LITTLE

    content_type = ImageContent

    @override
    def _parse(self):
        self.data.image = self.io.read()

        self.io.seek(16)
        self.data.width = self.io.value(F.U32, ByteOrder.BIG)
        self.data.height = self.io.value(F.U32, ByteOrder.BIG)
        self.data.bit_depth = self.io.value(F.U8)
        self.io.seek(self.io.size())
