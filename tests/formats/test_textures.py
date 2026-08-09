from pathlib import Path

import pytest

from scfile.formats import DdsEncoder, OlDecoder

from .conftest import ASSETS, export


ROOT = ASSETS / "textures"
SOURCES = tuple(sorted((ROOT / "source").glob("*.ol")))


@pytest.mark.parametrize("source", SOURCES)
def test_ol(
    source: Path,
) -> None:
    actual = export(OlDecoder, DdsEncoder, source)
    assert actual == (ROOT / "dds" / f"{source.stem}.dds").read_bytes()
