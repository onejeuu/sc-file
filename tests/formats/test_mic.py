from pathlib import Path

from scfile.formats.mic import MicDecoder
from scfile.formats.png import PngEncoder

from .conftest import extract


def test_image(assets: Path):
    src = "image/image"
    out = "image/image"
    source, output = extract(MicDecoder, PngEncoder, assets, src, out)
    assert source == output
