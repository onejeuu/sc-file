from pathlib import Path

import pytest

from scfile import convert
from scfile.exceptions import InvalidStructureError, UnsupportedFormatError
from tests.conftest import ASSETS, CUBEMAP, IMAGE, MODEL, MODEL_LEGACY, NBT, TEXTURE


FILES = sorted(path for path in (ASSETS / "cli").iterdir() if path.is_file())


@pytest.mark.parametrize("path", FILES)
def test_auto(temp: Path, path: Path):
    convert.auto(path, temp)


def test_formats_convert(temp: Path):
    src = ASSETS / "source" / MODEL
    out = temp / "model_v12.obj"
    convert.formats.mcsb_to_obj(src, temp)
    assert out.exists()

    src = ASSETS / "source" / MODEL_LEGACY
    out = temp / "model_v12.obj"
    convert.legacy.mcsa_to_obj(src, temp)
    assert out.exists()

    src = ASSETS / "source" / TEXTURE
    out = temp / "texture_dxt1.dds"
    convert.formats.ol_to_dds(src, temp)
    assert out.exists()

    src = ASSETS / "source" / CUBEMAP
    out = temp / "texture_cubemap.dds"
    convert.formats.ol_cubemap_to_dds(src, temp)
    assert out.exists()

    src = ASSETS / "source" / IMAGE
    out = temp / "image.png"
    convert.formats.mic_to_png(src, temp)
    assert out.exists()

    src = ASSETS / "source" / NBT
    out = temp / "nbt.json"
    convert.formats.nbt_to_json(src, temp)
    assert out.exists()


def test_auto_invalid_texture(temp: Path):
    with pytest.raises(InvalidStructureError):
        convert.auto(ASSETS / "invalid/broken.ol", temp)


def test_auto_unsupported(temp: Path):
    with pytest.raises(UnsupportedFormatError):
        convert.auto(ASSETS / "invalid/unknown.xyz", temp)
