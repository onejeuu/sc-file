from pathlib import Path

from scfile import convert


def test_convert_default(assets: Path, temp_file: str):
    convert.mcsa_to_obj(assets / "model.mcsa", temp_file)
    convert.ol_to_dds(assets / "texture.ol", temp_file)
    convert.mic_to_png(assets / "image.mic", temp_file)


def test_convert_ms3d(assets: Path, temp_file: str):
    convert.mcsa_to_ms3d(assets / "model.mcsa", temp_file)
    convert.mcsa_to_ms3d_ascii(assets / "model.mcsa", temp_file)


def test_convert_auto(assets: Path, temp_file: str):
    convert.auto(assets / "model.mcsa", temp_file)
