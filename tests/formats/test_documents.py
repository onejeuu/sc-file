import json
from pathlib import Path

import pytest

from scfile.exceptions import BinaryStructureError, SignatureMismatchError
from scfile.formats import HashmapDecoder, JsonEncoder, LangDecoder, SignDecoder

from .conftest import ASSETS, export


ROOT = ASSETS / "document"
SOURCE = ROOT / "source"


@pytest.mark.parametrize(
    ("decoder", "name"),
    ((HashmapDecoder, "mapping.map"), (SignDecoder, "textures.sign")),
)
def test_json(decoder: type[HashmapDecoder] | type[SignDecoder], name: str) -> None:
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


def test_sign() -> None:
    with SignDecoder(SOURCE / "textures.sign") as decoder:
        data = decoder.decode().value
        assert isinstance(data, dict)
        assert data["hash"] == b"abc"
        assert data["version"] == 1
        textures = data["textures"]
        assert isinstance(textures, list) and len(textures) == 1
        texture = textures[0]
        assert isinstance(texture, dict)
        mipmaps = texture["mipmaps"]
        assert isinstance(mipmaps, list)
        mipmap = mipmaps[0]
        assert isinstance(mipmap, dict)
        assert isinstance(mipmap["sha256"], bytes)
        assert decoder.io.eof()


def test_lang() -> None:
    expected = json.loads((ROOT / "json" / "translations.json").read_bytes())
    with LangDecoder(SOURCE / "translations.lang") as decoder:
        assert decoder.decode().value == expected


@pytest.mark.parametrize(
    ("decoder", "name"),
    ((HashmapDecoder, "truncated.map"), (SignDecoder, "truncated.sign"), (SignDecoder, "prefix.sign")),
)
def test_truncated(decoder: type[HashmapDecoder] | type[SignDecoder], name: str) -> None:
    with decoder(ROOT / "invalid" / name) as handler:
        with pytest.raises(BinaryStructureError):
            handler.decode()


def test_sign_signature() -> None:
    with SignDecoder(ROOT / "invalid" / "signature.sign") as decoder:
        with pytest.raises(SignatureMismatchError):
            decoder.decode()
