from pathlib import Path

import pytest

from scfile.formats.efkmodel.decoder import EfkmodelDecoder
from scfile.formats.hdri import OlCubemapDecoder
from scfile.formats.mcsb import McsbDecoder
from scfile.formats.mic import MicDecoder
from scfile.formats.nbt import NbtDecoder
from scfile.formats.ol import OlDecoder
from scfile.formats.texarr import TexarrDecoder
from tests.conftest import CUBEMAP, IMAGE, MODEL, MODEL_EFK, NBT, TEXARR, TEXTURE


@pytest.mark.parametrize(
    "decoder, src",
    [
        (McsbDecoder, MODEL),
        (EfkmodelDecoder, MODEL_EFK),
    ],
)
def test_sugar_model(assets: Path, decoder: type[McsbDecoder] | type[EfkmodelDecoder], src: str):
    with decoder(assets / "source" / src) as dec:
        with dec.to_obj() as enc:
            assert len(enc.getvalue()) > 0
        with dec.to_glb() as enc:
            assert len(enc.getvalue()) > 0
        with dec.to_fbx() as enc:
            assert len(enc.getvalue()) > 0
        with dec.to_dae() as enc:
            assert len(enc.getvalue()) > 0
        with dec.to_ms3d() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_texture(assets: Path):
    src = assets / "source" / TEXTURE
    with OlDecoder(src) as dec:
        with dec.to_dds() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_cubemap(assets: Path):
    src = assets / "source" / CUBEMAP
    with OlCubemapDecoder(src) as dec:
        with dec.to_dds() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_image(assets: Path):
    src = assets / "source" / IMAGE
    with MicDecoder(src) as dec:
        with dec.to_png() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_texarr(assets: Path):
    src = assets / "source" / TEXARR
    with TexarrDecoder(src) as dec:
        with dec.to_zip() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_nbt(assets: Path):
    src = assets / "source" / NBT
    with NbtDecoder(src) as dec:
        with dec.to_json() as enc:
            assert len(enc.getvalue()) > 0
