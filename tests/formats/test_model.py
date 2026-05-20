from pathlib import Path
from typing import Type

import pytest

from scfile.core import FileEncoder, ModelContent, UserOptions
from scfile.formats.dae import DaeEncoder
from scfile.formats.efkmodel import EfkmodelDecoder
from scfile.formats.fbx import FbxEncoder
from scfile.formats.glb import GlbEncoder
from scfile.formats.mcsb import McsbDecoder
from scfile.formats.ms3d import Ms3dEncoder
from scfile.formats.obj import ObjEncoder

from .conftest import extract


VERSIONS = [7, 8, 9, 10, 11, 12]
ENCODERS_FULL = [GlbEncoder, ObjEncoder]
ENCODERS_SMOKE = [DaeEncoder, FbxEncoder, Ms3dEncoder]

OPTIONS = UserOptions(parse_skeleton=True, parse_animation=True)

ModelEncoder = Type[FileEncoder[ModelContent]]


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_model(assets: Path, version: int, encoder: ModelEncoder):
    src = f"model/model_v{version}"
    out = f"model/model_v{version}{encoder.format.suffix}"
    source, output = extract(McsbDecoder, encoder, assets, src, out, OPTIONS)
    assert source == output


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("encoder", ENCODERS_SMOKE)
def test_model_smoke(assets: Path, version: int, encoder: ModelEncoder):
    src = f"model/model_v{version}"
    with McsbDecoder(assets / "source" / src, OPTIONS) as dec:
        data = dec.convert(encoder)
    assert len(data) > 0


@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_efkmodel(assets: Path, encoder: ModelEncoder):
    src = "model/efkmodel_v5"
    out = f"model/efkmodel_v5{encoder.format.suffix}"
    source, output = extract(EfkmodelDecoder, encoder, assets, src, out)
    assert source == output
