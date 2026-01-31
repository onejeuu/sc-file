from pathlib import Path

from scfile.formats.dds.encoder import DdsEncoder
from scfile.formats.ol.decoder import OlDecoder
from tests.codec.extract import extract


def test_ol_to_dds_dxt1(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, "dxt1/input", "dxt1/output")
    assert converted == expected


def test_ol_to_dds_dxt3(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, "dxt3/input", "dxt3/output")
    assert converted == expected


def test_ol_to_dds_dxt5(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, "dxt5/input", "dxt5/output")
    assert converted == expected


def test_ol_to_dds_rgba(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, "rgba/input", "rgba/output")
    assert converted == expected


def test_ol_to_dds_bgra(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, "bgra/input", "bgra/output")
    assert converted == expected


def test_ol_to_dds_dxnxy(assets: Path):
    converted, expected = extract(OlDecoder, DdsEncoder, assets, "dxnxy/input", "dxnxy/output")
    assert converted == expected
