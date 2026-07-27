from io import BytesIO
from pathlib import Path

import numpy as np
import pytest

from scfile.core import Options
from scfile.core.types import ModelEncoder
from scfile.exceptions import LimitError
from scfile.formats.dae import DaeEncoder
from scfile.formats.efkmodel import EfkmodelDecoder
from scfile.formats.fbx import FbxEncoder
from scfile.formats.glb import GlbEncoder
from scfile.formats.mcal.decoder import McalDecoder
from scfile.formats.mcsa.exceptions import McsaVersionUnsupported
from scfile.formats.mcsa.io import McsaFileIO
from scfile.formats.mcsb import McsbDecoder
from scfile.formats.ms3d import Ms3dEncoder
from scfile.formats.ms3d.exceptions import Ms3dCountsLimit
from scfile.formats.ms3d.io import Ms3dFileIO
from scfile.formats.obj import ObjEncoder
from tests.conftest import ASSETS

from .conftest import extract


VERSIONS = [7, 8, 9, 10, 11, 12]
ENCODERS_FULL = [GlbEncoder, ObjEncoder]
ENCODERS_SMOKE = [DaeEncoder, FbxEncoder, Ms3dEncoder]

SPECIALS = sorted((ASSETS / "source" / "model" / "special").iterdir())

OPTIONS = Options(skeleton=True, animation=True)


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
    opts = Options(skeleton=False)
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


def test_animodel():
    src = ASSETS / "source" / "model/animodel_v12"

    with McalDecoder(src) as dec:
        data = dec.decode()

    assert data.scene.scale.position == 2.0
    assert len(data.scene.animation.clips) >= 1


def test_invalid_version():
    with pytest.raises(McsaVersionUnsupported):
        McsbDecoder(ASSETS / "invalid" / "unsuported.mcsb").decode()


def test_invalid_counts():
    with pytest.raises(LimitError):
        McsbDecoder(ASSETS / "invalid" / "counts.mcsb").decode()


def test_invalid_counts_efkmodel():
    with pytest.raises(LimitError):
        EfkmodelDecoder(ASSETS / "invalid" / "counts.efkmodel").decode()


def test_ms3d_writecount_limit():
    class _Enc(Ms3dFileIO, BytesIO):
        pass

    with pytest.raises(Ms3dCountsLimit):
        _Enc()._writecount("vertices", 1000, 512)


def test_mcsa_readclip_scale():
    class _IO(McsaFileIO, BytesIO):
        pass

    frame = np.array([0, 0, 0, 16384, 16384, -16384, 32767], dtype="<i2")
    _, translations = _IO(frame.tobytes())._readclip(1, 1, 0, 2.0)

    assert np.allclose(translations[0, 0], frame[4:] * (2.0 / 32767.0))
