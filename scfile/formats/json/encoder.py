import json

from scfile.core import FileEncoder
from scfile.core.context import NbtContent
from scfile.enums import FileFormat


class JsonEncoder(FileEncoder[NbtContent]):
    format = FileFormat.JSON

    def serialize(self):
        data = json.dumps(self.data.value, default=str, ensure_ascii=False, indent=2)
        data = data.encode()
        self.write(data)
