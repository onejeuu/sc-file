from pathlib import Path

import pytest

from scfile.formats import EfkmodelDecoder, FbxEncoder, GlbEncoder, McalDecoder, McsaDecoder, McsbDecoder, McvdDecoder, ObjEncoder
from scfile.options import Options

from .conftest import ASSETS, assert_binary, export


ROOT = ASSETS / "models"
SOURCE = ROOT / "source"
OPTIONS = Options(model={"skeleton": True, "animation": True})

MCSB = tuple(sorted(SOURCE.glob("*.mcsb")))
ENCODERS = (("obj", ObjEncoder), ("glb", GlbEncoder), ("fbx", FbxEncoder))


@pytest.mark.parametrize("source", MCSB)
@pytest.mark.parametrize("folder, encoder", ENCODERS)
def test_mcsb(
    source: Path,
    folder: str,
    encoder: type[ObjEncoder] | type[GlbEncoder] | type[FbxEncoder],
) -> None:
    actual = export(McsbDecoder, encoder, source, OPTIONS)
    expected = (ROOT / folder / f"{source.name}{encoder.suffix()}").read_bytes()
    assert_binary(actual, expected)


@pytest.mark.parametrize("folder, encoder", ENCODERS)
def test_mcsa(
    folder: str,
    encoder: type[ObjEncoder] | type[GlbEncoder] | type[FbxEncoder],
) -> None:
    source = SOURCE / "model_v15.mcsa"
    actual = export(McsaDecoder, encoder, source, OPTIONS)
    expected = (ROOT / folder / f"{source.name}{encoder.suffix()}").read_bytes()
    assert_binary(actual, expected)


def test_mcvd() -> None:
    source = SOURCE / "animation.mcvd"
    actual = export(McvdDecoder, GlbEncoder, source, OPTIONS)
    assert_binary(actual, (ROOT / "glb" / f"{source.name}.glb").read_bytes())


def test_mcal() -> None:
    with McalDecoder(SOURCE / "library.mcal", OPTIONS) as decoder:
        content = decoder.decode()

    assert content.meta.counts.bones == 3
    assert [clip.name for clip in content.scene.animation.clips] == ["move"]


@pytest.mark.parametrize("folder, encoder", ENCODERS)
def test_efkmodel(
    folder: str,
    encoder: type[ObjEncoder] | type[GlbEncoder] | type[FbxEncoder],
) -> None:
    source = SOURCE / "particle.efkmodel"
    actual = export(EfkmodelDecoder, encoder, source)
    expected = (ROOT / folder / f"{source.name}{encoder.suffix()}").read_bytes()
    assert_binary(actual, expected)
