import json
from typing import override

from scfile.structures.content import DocumentContent
from scfile.core import Encoder
from scfile.enums import ByteOrder, FileFormat


class JsonEncoder(Encoder[DocumentContent]):
    format = FileFormat.JSON
    order = ByteOrder.LITTLE

    content_type = DocumentContent

    @override
    def _serialize(self):
        data = json.dumps(self.data.value, default=str, ensure_ascii=False, indent=2)
        data = data.encode()
        self.io.write(data)
