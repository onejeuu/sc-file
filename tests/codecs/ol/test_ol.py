from pathlib import Path

from scfile import DdsEncoder, OlDecoder
from tests.codecs.validate import validate_codec


def test_to_dds_dxt5(assets: Path):
    converted, expected = validate_codec(OlDecoder, DdsEncoder, assets, Path("dxt5"))
    assert converted == expected
