from pathlib import Path

from scfile.convert import formats, legacy
from scfile.convert.auto import auto
from scfile.core.context import UserOptions


def test_convert_formats(assets: Path, temp: Path, options: UserOptions):
    legacy.mcsa_to_dae(assets / "model.mcsa", temp, options)
    legacy.mcsa_to_glb(assets / "model.mcsa", temp, options)
    legacy.mcsa_to_ms3d(assets / "model.mcsa", temp, options)
    legacy.mcsa_to_obj(assets / "model.mcsa", temp, options)

    formats.ol_to_dds(assets / "texture.ol", temp, options)
    formats.mic_to_png(assets / "image.mic", temp, options)


def test_convert_auto(assets: Path, temp: Path, options: UserOptions):
    auto(assets / "model.mcsa", temp, options)
    auto(assets / "texture.ol", temp, options)
    auto(assets / "image.mic", temp, options)
