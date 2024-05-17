from pathlib import Path

from scfile import MicDecoder, PngEncoder
from tests.codecs.extract import extract


def test_to_png(assets: Path):
    converted, expected = extract(MicDecoder, PngEncoder, assets)
    assert converted == expected
