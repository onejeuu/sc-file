from dataclasses import dataclass, field

from scfile.core.content import FileContent, ModelContent
from scfile.core.decoder import FileDecoder
from scfile.core.encoder import FileEncoder
from scfile.enums import FileFormat, FileType


@dataclass
class FakeContent(FileContent):
    type: FileType = field(default=FileType.NONE)
    parsed: bytes = field(default_factory=bytes)


class FakeDecoder(FileDecoder[FakeContent]):
    format = FileFormat.MCSA
    signature = b"STRN"
    _content = FakeContent

    def parse(self) -> None:
        self.data.parsed = self.read()


class FakeEncoder(FileEncoder[FakeContent]):
    format = FileFormat.OBJ
    signature = b"HXGN"

    def serialize(self) -> None:
        self.write(self.data.parsed)


class FakeModelEncoder(FileEncoder[ModelContent]):
    format = FileFormat.OBJ

    def serialize(self) -> None:
        pass
