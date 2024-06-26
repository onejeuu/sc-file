from pathlib import Path

from scfile import DdsEncoder, OlDecoder
from tests.codec.extract import extract


def test_to_dds_dxt1(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxt1"))
    assert converted == expected


def test_to_dds_dxt5(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxt5"))
    assert converted == expected
