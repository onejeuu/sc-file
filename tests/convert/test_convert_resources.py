from pathlib import Path

import pytest

from scfile.content import BaseContent
from scfile.core import Decoder, Encoder, Resources
from scfile.enums import FileFormat


class DummyContent(BaseContent):
    pass


instances: dict[str, Decoder | Encoder] = {}


class DummyDecoder(Decoder[DummyContent]):
    content_type = DummyContent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instances["decoder"] = self

    def _parse(self) -> None:
        pass


class DummyEncoder(Encoder[DummyContent]):
    content_type = DummyContent
    format = FileFormat.JSON

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instances["encoder"] = self

    def _serialize(self) -> None:
        self.io.write(b"encoded")


def test_manual_conversion_shares_resources(tmp_path: Path) -> None:
    pytest.importorskip("zstandard")
    from scfile.convert.files import manual

    instances.clear()
    source = tmp_path / "source.bin"
    output = tmp_path / "target.json"
    source.write_bytes(b"source")
    resources = Resources({"example": object()})

    result = manual(DummyDecoder, DummyEncoder, source, output, resources=resources)

    assert result == output
    assert output.read_bytes() == b"encoded"
    assert instances["decoder"].resources is resources
    assert instances["encoder"].resources is resources


def test_manual_conversion_creates_one_shared_resources_container(tmp_path: Path) -> None:
    pytest.importorskip("zstandard")
    from scfile.convert.files import manual

    instances.clear()
    source = tmp_path / "source.bin"
    output = tmp_path / "target.json"
    source.write_bytes(b"source")

    manual(DummyDecoder, DummyEncoder, source, output)

    assert instances["decoder"].resources is instances["encoder"].resources
