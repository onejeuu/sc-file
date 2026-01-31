from pathlib import Path

from scfile.formats.mic.decoder import MicDecoder
from scfile.formats.png.encoder import PngEncoder
from tests.codec.extract import extract


def test_mic_to_png(assets: Path):
    converted, expected = extract(MicDecoder, PngEncoder, assets)
    assert converted == expected
