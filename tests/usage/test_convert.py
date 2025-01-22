from pathlib import Path

from scfile import convert


def test_convert_formats(assets: Path, temp: Path):
    convert.formats.mcsa_to_obj(assets / "model.mcsa", temp, overwrite=True)
    convert.formats.ol_to_dds(assets / "texture.ol", temp, overwrite=True)
    convert.formats.mic_to_png(assets / "image.mic", temp, overwrite=True)
    convert.formats.mcsa_to_ms3d(assets / "model.mcsa", temp, overwrite=True)


def test_convert_auto(assets: Path, temp: Path):
    convert.auto(assets / "model.mcsa", temp, overwrite=True)
