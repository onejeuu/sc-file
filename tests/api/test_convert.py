from pathlib import Path

import pytest

from scfile import convert
from scfile.exceptions import InvalidStructureError, UnsupportedFormatError
from tests.conftest import CUBEMAP, IMAGE, MODEL, MODEL_LEGACY, NBT, TEXTURE


def test_formats_convert(assets: Path, temp: Path):
    src = assets / "source" / MODEL
    out = temp / "model_v12.obj"
    convert.formats.mcsb_to_obj(src, temp)
    assert out.exists()

    src = assets / "source" / MODEL_LEGACY
    out = temp / "model_v12.obj"
    convert.legacy.mcsa_to_obj(src, temp)
    assert out.exists()

    src = assets / "source" / TEXTURE
    out = temp / "texture_dxt1.dds"
    convert.formats.ol_to_dds(src, temp)
    assert out.exists()

    src = assets / "source" / CUBEMAP
    out = temp / "texture_cubemap.dds"
    convert.formats.ol_cubemap_to_dds(src, temp)
    assert out.exists()

    src = assets / "source" / IMAGE
    out = temp / "image.png"
    convert.formats.mic_to_png(src, temp)
    assert out.exists()

    src = assets / "source" / NBT
    out = temp / "nbt.json"
    convert.formats.nbt_to_json(src, temp)
    assert out.exists()


def test_auto(assets: Path, temp: Path):
    for path in (assets / "cli").iterdir():
        if path.is_file():
            convert.auto(path, temp)


def test_auto_invalid_texture(assets: Path, temp: Path):
    with pytest.raises(InvalidStructureError):
        convert.auto(assets / "invalid" / "broken.ol", temp)


def test_auto_unsupported(assets: Path, temp: Path):
    with pytest.raises(UnsupportedFormatError):
        convert.auto(assets / "invalid" / "unknown.xyz", temp)
