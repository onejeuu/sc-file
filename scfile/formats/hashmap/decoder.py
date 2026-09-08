from typing import override

from scfile.content import DocumentContent
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat


class HashmapDecoder(Decoder[DocumentContent]):
    format = FileFormat.MAP
    order = ByteOrder.BIG

    content_type = DocumentContent

    @override
    def _parse(self):
        count = self.io.value(F.U32)
        self.data.value = {self.io.string(): self.io.read_exact(20) for _ in range(count)}
