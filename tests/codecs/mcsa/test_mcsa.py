from pathlib import Path

from scfile import McsaDecoder, ObjEncoder
from tests.codecs.validate import validate_codec


def test_to_mcsa_v7(assets: Path):
    converted, expected = validate_codec(McsaDecoder, ObjEncoder, assets, Path("v7"))
    assert converted == expected
