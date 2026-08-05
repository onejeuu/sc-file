import json
from typing import override

from scfile.core import DocumentContent, Encoder
from scfile.enums import ByteOrder, FileFormat


class JsonEncoder(Encoder[DocumentContent]):
    content_type = DocumentContent
    format = FileFormat.JSON
    order = ByteOrder.LITTLE

    @override
    def _serialize(self):
        data = json.dumps(self.data.value, default=str, ensure_ascii=False, indent=2)
        data = data.encode()
        self.io.write(data)
