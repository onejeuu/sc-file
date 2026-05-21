from scfile.formats.mic import MicDecoder
from scfile.formats.png import PngEncoder

from .conftest import extract


def test_image():
    src = "image/image"
    out = "image/image"
    source, output = extract(MicDecoder, PngEncoder, src, out)
    assert source == output
