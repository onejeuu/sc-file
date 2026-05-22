import pytest

from scfile.formats.dds import DdsEncoder
from scfile.formats.hdri import OlCubemapDecoder
from scfile.formats.ol import OlDecoder
from scfile.formats.ol.exceptions import OlFormatUnsupported
from tests.conftest import ASSETS

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
def test_texture(name: str):
    src = f"texture/{name}"
    out = f"texture/{name}"
    source, output = extract(OlDecoder, DdsEncoder, src, out)
    assert source == output


def test_cubemap():
    src = "texture/texture_cubemap"
    out = "texture/texture_cubemap"
    source, output = extract(OlCubemapDecoder, DdsEncoder, src, out)
    assert source == output


def test_invalid_version():
    with pytest.raises(OlFormatUnsupported):
        OlDecoder(ASSETS / "invalid" / "unsuported.ol").decode()
