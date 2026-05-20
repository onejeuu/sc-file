from pathlib import Path
from typing import Type

import pytest

from scfile.core import FileEncoder, ModelContent
from scfile.formats.glb import GlbEncoder
from scfile.formats.mcsb import McsbDecoder
from scfile.formats.obj import ObjEncoder

from .conftest import extract


ENCODERS = [GlbEncoder, ObjEncoder]


@pytest.mark.parametrize("version", [7, 8, 9, 10, 11, 12])
@pytest.mark.parametrize("encoder", ENCODERS)
def test_model(assets: Path, version: int, encoder: Type[FileEncoder[ModelContent]]):
    src = f"model/model_v{version}"
    out = f"model/model_v{version}{encoder.format.suffix}"
    source, output = extract(McsbDecoder, encoder, assets, src, out)
    assert source == output
