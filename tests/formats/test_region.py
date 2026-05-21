from scfile.formats.mca import McaEncoder
from scfile.formats.mdat import MdatDecoder

from .conftest import extract


def test_region():
    src = "region/region"
    out = "region/region"
    source, output = extract(MdatDecoder, McaEncoder, src, out)
    assert source == output
