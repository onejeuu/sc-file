from pathlib import Path

from scfile.formats.mca import McaEncoder
from scfile.formats.mdat import MdatDecoder

from .conftest import extract


def test_region(assets: Path):
    src = "region/region"
    out = "region/region"
    source, output = extract(MdatDecoder, McaEncoder, assets, src, out)
    assert source == output
