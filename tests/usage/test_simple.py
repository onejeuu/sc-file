from pathlib import Path

from scfile import convert


def test_convert_default(assets: Path, temp: Path):
    convert.mcsa_to_obj(assets / "model.mcsa", temp, overwrite=True)
    convert.ol_to_dds(assets / "texture.ol", temp, overwrite=True)
    convert.mic_to_png(assets / "image.mic", temp, overwrite=True)


def test_convert_ms3d(assets: Path, temp: Path):
    convert.mcsa_to_ms3d(assets / "model.mcsa", temp, overwrite=True)
    convert.mcsa_to_ms3d_ascii(assets / "model.mcsa", temp, overwrite=True)


def test_convert_auto(assets: Path, temp: Path):
    convert.auto(assets / "model.mcsa", temp, overwrite=True)
