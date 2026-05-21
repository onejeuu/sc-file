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
from tests.conftest import ASSETS

from .conftest import extract


VERSIONS = [7, 8, 9, 10, 11, 12]
ENCODERS_FULL = [GlbEncoder, ObjEncoder]
ENCODERS_SMOKE = [DaeEncoder, FbxEncoder, Ms3dEncoder]

SPECIALS = sorted((ASSETS / "source" / "model" / "special").iterdir())

OPTIONS = UserOptions(parse_skeleton=True, parse_animation=True)


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_model(version: int, encoder: ModelEncoder):
    src = f"model/model_v{version}"
    out = f"model/model_v{version}{encoder.format.suffix}"
    source, output = extract(McsbDecoder, encoder, src, out, OPTIONS)
    assert source == output


@pytest.mark.parametrize("path", SPECIALS)
@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_model_special(path: Path, encoder: ModelEncoder):
    src = f"model/special/{path.stem}"
    out = f"model/special/{path.stem}{encoder.format.suffix}"
    source, output = extract(McsbDecoder, encoder, src, out, OPTIONS)
    assert source == output


@pytest.mark.parametrize("name", ["model_v12_links2", "model_v12_links3"])
def test_skip_links(name: str):
    src = ASSETS / "source" / "model" / "special" / name
    opts = UserOptions(parse_skeleton=False)
    with McsbDecoder(src, opts) as dec:
        data = dec.decode()
    assert len(data.scene.meshes) > 0


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("encoder", ENCODERS_SMOKE)
def test_model_smoke(version: int, encoder: ModelEncoder):
    src = ASSETS / "source" / f"model/model_v{version}"
    with McsbDecoder(src, OPTIONS) as dec:
        data = dec.convert(encoder)
    assert len(data) > 0


@pytest.mark.parametrize("encoder", ENCODERS_FULL)
def test_efkmodel(encoder: ModelEncoder):
    src = "model/efkmodel_v5"
    out = f"model/efkmodel_v5{encoder.format.suffix}"
    source, output = extract(EfkmodelDecoder, encoder, src, out)
    assert source == output
