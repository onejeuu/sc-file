import json
from pathlib import Path
from typing import cast

import pytest

from scfile.exceptions import BinaryStructureError
from scfile.formats import HashmapDecoder, JsonEncoder, LangDecoder, NbtDecoder, SignDecoder

from .conftest import ASSETS, export


ROOT = ASSETS / "document"
SOURCE = ROOT / "source"


@pytest.mark.parametrize(
    ("decoder", "name"),
    ((HashmapDecoder, "mapping.map"),),
)
def test_hashmap_json(decoder: type[HashmapDecoder], name: str) -> None:
    actual = export(decoder, JsonEncoder, SOURCE / name)
    expected = (ROOT / "json" / f"{Path(name).stem}.json").read_bytes()
    assert json.loads(actual) == json.loads(expected)


@pytest.mark.parametrize("source", sorted(SOURCE.glob("*.nbt*")))
def test_nbt_documents(source: Path) -> None:
    actual = export(NbtDecoder, JsonEncoder, source)
    expected = (ROOT / "json" / "document.json").read_bytes()

    assert json.loads(actual) == json.loads(expected)


def test_lang_entries() -> None:
    with LangDecoder(SOURCE / "strings.lang") as decoder:
        data = decoder.decode().value

    assert data == {"hello": "world", "empty": ""}


def test_sign_texture_metadata() -> None:
    with SignDecoder(SOURCE / "textures.sign") as decoder:
        data = cast(dict[str, object], decoder.decode().value)

    assert data["hash"] == b"abc"
    assert data["version"] == 7
    textures = cast(list[dict[str, object]], data["textures"])
    assert textures == [
        {
            "path": "texture.ol",
            "height": 64,
            "width": 128,
            "mipmap_count": 2,
            "face_count": 1,
            "format": "DXT1",
            "mipmaps": [
                {
                    "index": 0,
                    "cube_face": 0,
                    "compressed_size": 16,
                    "uncompressed_size": 32,
                    "sha256": b"a" * 32,
                }
            ],
        }
    ]


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
