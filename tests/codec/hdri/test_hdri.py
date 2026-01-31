from pathlib import Path

from scfile.formats.dds.encoder import DdsEncoder
from scfile.formats.hdri.decoder import OlCubemapDecoder
from tests.codec.extract import extract


def test_hdri_to_dds_cubemap_dxt5(assets: Path):
    converted, expected = extract(OlCubemapDecoder, DdsEncoder, assets)
    assert converted == expected
