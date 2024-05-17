from pathlib import Path

from scfile import MicDecoder, PngEncoder
from tests.codecs.validate import validate_codec


def test_to_png(assets: Path):
    converted, expected = validate_codec(MicDecoder, PngEncoder, assets)
    assert converted == expected
