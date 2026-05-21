from pathlib import Path

import pytest

from scfile.formats.efkmodel.decoder import EfkmodelDecoder
from scfile.formats.hdri import OlCubemapDecoder
from scfile.formats.mcsb import McsbDecoder
from scfile.formats.mic import MicDecoder
from scfile.formats.nbt import NbtDecoder
from scfile.formats.ol import OlDecoder
from scfile.formats.texarr import TexarrDecoder
from tests.conftest import ASSETS, CUBEMAP, IMAGE, MODEL, MODEL_EFK, NBT, TEXARR, TEXTURE


@pytest.mark.parametrize(
    "decoder, src",
    [
        (McsbDecoder, MODEL),
        (EfkmodelDecoder, MODEL_EFK),
    ],
)
def test_sugar_model(decoder: type[McsbDecoder] | type[EfkmodelDecoder], src: str):
    with decoder(ASSETS / "source" / src) as dec:
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


def test_sugar_texture():
    src = ASSETS / "source" / TEXTURE
    with OlDecoder(src) as dec:
        with dec.to_dds() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_cubemap():
    src = ASSETS / "source" / CUBEMAP
    with OlCubemapDecoder(src) as dec:
        with dec.to_dds() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_image():
    src = ASSETS / "source" / IMAGE
    with MicDecoder(src) as dec:
        with dec.to_png() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_texarr():
    src = ASSETS / "source" / TEXARR
    with TexarrDecoder(src) as dec:
        with dec.to_zip() as enc:
            assert len(enc.getvalue()) > 0


def test_sugar_nbt():
    src = ASSETS / "source" / NBT
    with NbtDecoder(src) as dec:
        with dec.to_json() as enc:
            assert len(enc.getvalue()) > 0
