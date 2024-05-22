from pathlib import Path

from scfile import McsaDecoder, ObjEncoder
from tests.codec.extract import extract


def test_to_obj_v7(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, Path("v7"), "output_obj")
    assert converted == expected


def test_to_obj_v8(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, Path("v8"), "output_obj")
    assert converted == expected


def test_to_obj_v10(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, Path("v10"), "output_obj")
    assert converted == expected
