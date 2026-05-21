from pathlib import Path

import pytest

from scfile.core import UserOptions
from scfile.core.types import ModelEncoder
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
SPECIAL = ["model_v12_links2", "model_v12_links3", "model_v12_links4", "model_v12_quads"]

OPTIONS = UserOptions(parse_skeleton=True, parse_animation=True)


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_model(assets: Path, version: int, encoder: ModelEncoder):
    src = f"model/model_v{version}"
    out = f"model/model_v{version}{encoder.format.suffix}"
    source, output = extract(McsbDecoder, encoder, assets, src, out, OPTIONS)
    assert source == output


@pytest.mark.parametrize("filename", SPECIAL)
@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_model_special(assets: Path, filename: str, encoder: ModelEncoder):
    src = f"model/special/{filename}"
    out = f"model/special/{filename}{encoder.format.suffix}"
    source, output = extract(McsbDecoder, encoder, assets, src, out, OPTIONS)
    assert source == output


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("encoder", ENCODERS_SMOKE)
def test_model_smoke(assets: Path, version: int, encoder: ModelEncoder):
    src = assets / "source" / f"model/model_v{version}"
    with McsbDecoder(src, OPTIONS) as dec:
        data = dec.convert(encoder)
    assert len(data) > 0


@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_efkmodel(assets: Path, encoder: ModelEncoder):
    src = "model/efkmodel_v5"
    out = f"model/efkmodel_v5{encoder.format.suffix}"
    source, output = extract(EfkmodelDecoder, encoder, assets, src, out)
    assert source == output
