import json
from pathlib import Path

import pytest

from scfile.exceptions import BinaryStructureError
from scfile.formats import HashmapDecoder, JsonEncoder, LangDecoder, SignDecoder

from .conftest import ASSETS, export


ROOT = ASSETS / "document"
SOURCE = ROOT / "source"


@pytest.mark.parametrize(
    ("decoder", "name"),
    ((HashmapDecoder, "mapping.map"),),
)
def test_json(decoder: type[HashmapDecoder] | type[SignDecoder] | type[LangDecoder], name: str) -> None:
    actual = export(decoder, JsonEncoder, SOURCE / name)
    expected = (ROOT / "json" / f"{Path(name).stem}.json").read_bytes()
    assert json.loads(actual) == json.loads(expected)


def test_hashmap() -> None:
    with HashmapDecoder(SOURCE / "mapping.map") as decoder:
        data = decoder.decode().value
        assert isinstance(data, dict)
        assert len(data) == 2
        assert data["путь/file"] == bytes.fromhex("28292a2b2c2d2e2f303132333435363738393a3b")
        assert isinstance(data["other/file"], bytes)
        assert decoder.io.eof()


@pytest.mark.parametrize(
    ("decoder", "name"),
    ((HashmapDecoder, "truncated.map"),),
)
def test_truncated(decoder: type[HashmapDecoder] | type[SignDecoder], name: str) -> None:
    with decoder(ROOT / "invalid" / name) as handler:
        with pytest.raises(BinaryStructureError):
            handler.decode()
