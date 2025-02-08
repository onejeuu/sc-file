from pathlib import Path

from scfile.formats.dds.encoder import DdsEncoder
from scfile.formats.ol.decoder import OlDecoder
from tests.codec.extract import extract


def test_to_dds_dxt1(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxt1"))
    assert converted == expected


def test_to_dds_dxt3(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxt3"))
    assert converted == expected


def test_to_dds_dxt5(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxt5"))
    assert converted == expected


def test_to_dds_rgba(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("rgba"))
    assert converted == expected


def test_to_dds_bgra(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("bgra"))
    assert converted == expected


def test_to_dds_dxnxy(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxnxy"))
    assert converted == expected
