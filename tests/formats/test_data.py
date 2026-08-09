from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from scfile.formats import (
    JsonEncoder,
    McaEncoder,
    MdatDecoder,
    MicDecoder,
    NbtDecoder,
    PngEncoder,
    TexarrDecoder,
    ZipEncoder,
)

from .conftest import ASSETS, export


def test_mic() -> None:
    root = ASSETS / "image"
    assert export(MicDecoder, PngEncoder, root / "source" / "screen.mic") == (root / "png" / "screen.png").read_bytes()


@pytest.mark.parametrize("source", sorted((ASSETS / "document" / "source").glob("*.nbt*")))
def test_nbt(
    source: Path,
) -> None:
    root = ASSETS / "document"
    actual = export(NbtDecoder, JsonEncoder, source)
    expected = (root / "json" / "document.json").read_bytes()
    assert json.loads(actual) == json.loads(expected)


def test_mdat() -> None:
    root = ASSETS / "region"
    actual = export(MdatDecoder, McaEncoder, root / "source" / "r.0.0.mdat")
    assert actual == (root / "mca" / "r.0.0.mca").read_bytes()


def test_texarr() -> None:
    root = ASSETS / "archive"
    actual = export(TexarrDecoder, ZipEncoder, root / "source" / "textures.texarr")
    expected = (root / "zip" / "textures.zip").read_bytes()

    with ZipFile(BytesIO(actual)) as result, ZipFile(BytesIO(expected)) as reference:
        assert result.namelist() == reference.namelist()
        for name in result.namelist():
            assert result.read(name) == reference.read(name)
