from pathlib import Path

from scfile import McsaDecoder, ObjEncoder
from tests.codec.extract import extract


def test_to_obj_v7(assets: Path):
    converted, expected = extract(McsaDecoder, ObjEncoder, assets, Path("v7"))
    assert converted == expected
