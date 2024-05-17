from pathlib import Path

from scfile import DdsEncoder, OlDecoder
from tests.codecs.extract import extract


def test_to_dds_dxt5(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, Path("dxt5"))
    assert converted == expected
