from typing import override

from scfile import formats
from scfile.consts import FileSignature
from scfile.core import Decoder, ImageContent
from scfile.enums import ByteOrder, FileFormat


class MicDecoder(Decoder[ImageContent]):
    format = FileFormat.MIC
    signature = FileSignature.MIC
    order = ByteOrder.LITTLE

    content_type = ImageContent

    def as_png(self):
        return self.convert_to(formats.png.PngEncoder)

    @override
    def _parse(self):
        self.data.image = self.io.read()
