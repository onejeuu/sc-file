from pathlib import Path

from scfile.formats.mic import MicDecoder
from scfile.formats.png import PngEncoder

from .conftest import extract


def test_image(assets: Path):
    source, output = extract(MicDecoder, PngEncoder, assets, "image", "image")
    assert source == output
