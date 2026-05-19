from pathlib import Path

from scfile.formats.dds import DdsEncoder
from scfile.formats.hdri import OlCubemapDecoder
from scfile.formats.ol import OlDecoder

from .conftest import extract


def test_dxt1(assets: Path):
    source, output = extract(OlDecoder, DdsEncoder, assets, "texture_dxt1", "texture_dxt1")
    assert source == output


def test_dxt3(assets: Path):
    source, output = extract(OlDecoder, DdsEncoder, assets, "texture_dxt3", "texture_dxt3")
    assert source == output


def test_dxt5(assets: Path):
    source, output = extract(OlDecoder, DdsEncoder, assets, "texture_dxt5", "texture_dxt5")
    assert source == output


def test_rgba(assets: Path):
    source, output = extract(OlDecoder, DdsEncoder, assets, "texture_rgba", "texture_rgba")
    assert source == output


def test_bgra(assets: Path):
    source, output = extract(OlDecoder, DdsEncoder, assets, "texture_bgra", "texture_bgra")
    assert source == output


def test_dxnxy(assets: Path):
    source, output = extract(OlDecoder, DdsEncoder, assets, "texture_dxnxy", "texture_dxnxy")
    assert source == output


def test_cubemap(assets: Path):
    source, output = extract(OlCubemapDecoder, DdsEncoder, assets, "texture_cubemap", "texture_cubemap")
    assert source == output
