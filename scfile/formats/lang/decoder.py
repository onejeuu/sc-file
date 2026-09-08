from typing import override

from scfile.content import DocumentContent
from scfile.content.base import DocumentValue
from scfile.core import Decoder
from scfile.enums import ByteOrder, FileFormat


class LangDecoder(Decoder[DocumentContent]):
    format = FileFormat.LANG
    order = ByteOrder.LITTLE

    content_type = DocumentContent
    standalone = False

    @override
    def _parse(self):
        data: dict[str, DocumentValue] = {}
        text = self.io.read().decode("utf-8", errors=self.io.errors)

        for line in text.splitlines():
            if not line or line.lstrip().startswith("#"):
                continue

            key, separator, value = line.partition("=")
            if separator:
                data[key] = value

        self.data.value = data
