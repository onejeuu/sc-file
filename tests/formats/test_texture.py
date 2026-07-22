import pytest

from scfile.formats.dds import DdsEncoder
from scfile.formats.ol import OlDecoder
from scfile.formats.ol.exceptions import OlFormatUnsupported, OlKindUnsupported
from scfile.structures.textures import CubemapTexture, DefaultTexture
from tests.conftest import ASSETS

from .conftest import extract


TEXTURES = [
    "texture_dxt1",
    "texture_dxt3",
    "texture_dxt5",
    "texture_dxnx",
    "texture_dxnxy",
    "texture_bgra",
    "texture_rgba",
    "texture_rgba32f",
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
    source, output = extract(OlDecoder, DdsEncoder, src, out)
    assert source == output


def test_kind():
    with OlDecoder(ASSETS / "source" / "texture/texture_dxt1") as decoder:
        texture = decoder.decode().texture
    assert isinstance(texture, DefaultTexture)

    with OlDecoder(ASSETS / "source" / "texture/texture_cubemap") as decoder:
        texture = decoder.decode().texture
    assert isinstance(texture, CubemapTexture)


def test_unsupported_kind():
    source = bytearray((ASSETS / "source" / "texture/texture_dxt1").read_bytes())
    source[32] = 2

    with pytest.raises(OlKindUnsupported):
        OlDecoder(bytes(source)).decode()


def test_invalid_version():
    with pytest.raises(OlFormatUnsupported):
        OlDecoder(ASSETS / "invalid" / "unsuported.ol").decode()
