from dataclasses import dataclass
from typing import ClassVar

from scfile.content import BaseContent
from scfile.core import Decoder, Encoder
from scfile.enums import FileFormat, FileKind


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


def pytest_assertrepr_compare(op: str, left: object, right: object) -> list[str] | None:
    if op != "==" or type(left) is not bytes or type(right) is not bytes:
        return None

    shared = min(len(left), len(right))
    offset = next((index for index in range(shared) if left[index] != right[index]), shared)
    actual = f"0x{left[offset]:02X}" if offset < len(left) else "EOF"
    expected = f"0x{right[offset]:02X}" if offset < len(right) else "EOF"
    return [
        "binary data differs",
        f"first difference: offset {offset:,}, actual {actual}, expected {expected}",
        f"length: actual {len(left):,}, expected {len(right):,}",
    ]
