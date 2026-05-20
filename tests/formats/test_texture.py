from pathlib import Path

import pytest

from scfile.formats.dds import DdsEncoder
from scfile.formats.hdri import OlCubemapDecoder
from scfile.formats.ol import OlDecoder

from .conftest import extract


TEXTURES = [
    "texture_dxt1",
    "texture_dxt3",
    "texture_dxt5",
    "texture_rgba",
    "texture_bgra",
    "texture_dxnxy",
]


@pytest.mark.parametrize("name", TEXTURES)
def test_texture(assets: Path, name: str):
    src = f"texture/{name}"
    out = f"texture/{name}"
    source, output = extract(OlDecoder, DdsEncoder, assets, src, out)
    assert source == output


def test_cubemap(assets: Path):
    src = "texture/texture_cubemap"
    out = "texture/texture_cubemap"
    source, output = extract(OlCubemapDecoder, DdsEncoder, assets, src, out)
    assert source == output
