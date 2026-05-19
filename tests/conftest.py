import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

import pytest

from scfile.core.content import FileContent, ModelContent
from scfile.core.decoder import FileDecoder
from scfile.core.encoder import FileEncoder
from scfile.enums import FileFormat, FileType


@pytest.fixture
def temp() -> Generator[Path, None, None]:
    path = Path(tempfile.mkdtemp(prefix="scfiletest"))
    yield path
    shutil.rmtree(path)


@dataclass
class FakeContent(FileContent):
    type: FileType = field(default=FileType.NONE)
    parsed: bytes = field(default_factory=bytes)


class FakeDecoder(FileDecoder[FakeContent]):
    format = FileFormat.MCSA
    _content = FakeContent

    def parse(self) -> None:
        self.data.parsed = self.read()


class FakeEncoder(FileEncoder[FakeContent]):
    format = FileFormat.OBJ

    def serialize(self) -> None:
        self.write(self.data.parsed)


class FakeModelEncoder(FileEncoder[ModelContent]):
    format = FileFormat.OBJ

    def serialize(self) -> None:
        pass
