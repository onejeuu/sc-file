from pathlib import Path
from struct import unpack_from

import pytest

from scfile.content.textures import CubemapTexture, DefaultTexture
from scfile.formats import DdsEncoder, MicDecoder, OlDecoder, PngEncoder
from scfile.options import Options

from .conftest import ASSETS, export


ROOT = ASSETS / "textures"
SOURCES = tuple(sorted((ROOT / "source").glob("*.ol")))
IMAGE_ROOT = ASSETS / "image"


@pytest.mark.parametrize("source", SOURCES)
def test_ol(
    source: Path,
) -> None:
    actual = export(OlDecoder, DdsEncoder, source)
    assert actual == (ROOT / "dds" / f"{source.stem}.dds").read_bytes()


def test_mic_to_png() -> None:
    source = IMAGE_ROOT / "source" / "screen.mic"

    assert export(MicDecoder, PngEncoder, source) == (IMAGE_ROOT / "png" / "screen.png").read_bytes()


@pytest.mark.parametrize(
    ("source", "texture_type"),
    (
        (ROOT / "source/texture_dxt1.ol", DefaultTexture),
        (ROOT / "source/texture_cubemap.ol", CubemapTexture),
    ),
)
def test_mipmap_limit(source: Path, texture_type: type[DefaultTexture | CubemapTexture]) -> None:
    options = Options(ol_max_mipmaps=1)

    with OlDecoder(source, options) as decoder:
        content = decoder.decode()

    assert isinstance(content.texture, texture_type)
    assert content.meta.mipmap_count > content.texture.mipmap_count
    assert content.texture.mipmap_count == 1

    with DdsEncoder(content, options) as encoder:
        dds = encoder.to_bytes()

    assert unpack_from("<I", dds, 28) == (1,)


def test_texture_metadata() -> None:
    source = ROOT / "source/texture_dxt1.ol"

    with OlDecoder(source, Options(ol_max_mipmaps=0)) as decoder:
        content = decoder.decode()
        assert decoder.io.tell() < decoder.io.size()

    assert content.width > 0
    assert content.height > 0
    assert content.meta.mipmap_count > 0
    assert content.texture.mipmap_count == 0

