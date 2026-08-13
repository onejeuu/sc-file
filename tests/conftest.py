from dataclasses import dataclass
from typing import ClassVar

from scfile.core import Decoder, Encoder
from scfile.enums import FileFormat, FileKind
from scfile.structures.content import BaseContent


@dataclass
class StubContent(BaseContent):
    kind: ClassVar[FileKind] = FileKind.NONE

    payload: bytes = b""


class BytesDecoder(Decoder[StubContent]):
    format: ClassVar[FileFormat] = FileFormat.NONE
    signature = b"STRN"
    content_type = StubContent

    def _parse(self) -> None:
        self.data.payload = self.io.read()


class BytesEncoder(Encoder[StubContent]):
    format: ClassVar[FileFormat] = FileFormat.NONE
    signature = b"HXGN"
    content_type = StubContent

    def _serialize(self) -> None:
        self.io.write(self.data.payload)
