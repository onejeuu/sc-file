from pathlib import Path

from scfile.formats.mcsa.decoder import McsaDecoder
from scfile.formats.obj.encoder import ObjEncoder
from tests.codec.extract import extract


def test_mcsa_to_obj_v7(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, "v7/input", "v7/output")
    assert converted == expected


def test_mcsa_to_obj_v8(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, "v8/input", "v8/output")
    assert converted == expected


def test_mcsa_to_obj_v10(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, "v10/input", "v10/output")
    assert converted == expected


def test_mcsa_to_obj_v11(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, "v11/input", "v11/output")
    assert converted == expected
