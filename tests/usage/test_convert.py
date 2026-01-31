from pathlib import Path

from scfile import UserOptions, convert


def test_convert_formats(assets: Path, temp: Path, options: UserOptions):
    convert.legacy.mcsa_to_obj(assets / "model.mcsa", temp, options)
    convert.legacy.mcsa_to_glb(assets / "model.mcsa", temp, options)
    convert.legacy.mcsa_to_dae(assets / "model.mcsa", temp, options)
    convert.legacy.mcsa_to_ms3d(assets / "model.mcsa", temp, options)

    convert.formats.ol_to_dds(assets / "texture.ol", temp, options)
    convert.formats.ol_cubemap_to_dds(assets / "cubemap.ol", temp, options)

    convert.formats.mic_to_png(assets / "image.mic", temp, options)

    convert.formats.texarr_to_zip(assets / "blocks.texarr", temp, options)

    convert.formats.nbt_to_json(assets / "itemnames.dat", temp, options)
    convert.formats.nbt_to_json(assets / "common", temp, options)


def test_convert_auto(assets: Path, temp: Path, options: UserOptions):
    convert.auto(assets / "model.mcsa", temp, options)
    convert.auto(assets / "texture.ol", temp, options)
    convert.auto(assets / "cubemap.ol", temp, options)
    convert.auto(assets / "image.mic", temp, options)
    convert.auto(assets / "blocks.texarr", temp, options)
    convert.auto(assets / "itemnames.dat", temp, options)
    convert.auto(assets / "common", temp, options)
