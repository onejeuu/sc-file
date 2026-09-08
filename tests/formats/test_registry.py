from scfile.enums import FileFormat
from scfile.formats import registry


def test_handlers() -> None:
    assert registry.decoders[FileFormat.MCSB].format is FileFormat.MCSB
    assert registry.encoders[FileFormat.GLB].format is FileFormat.GLB


def test_match() -> None:
    assert registry.match("model.mcsb") is registry.decoders[FileFormat.MCSB]
    assert registry.match("data/itemnames.dat") is registry.decoders[FileFormat.NBT]
    assert registry.match("en.lang") is registry.decoders[FileFormat.LANG]
    assert registry.match("textures.sign") is registry.decoders[FileFormat.SIGN]
    assert registry.match("stalcraft.map") is registry.decoders[FileFormat.MAP]
    assert registry.match("unknown.bin") is None


def test_filters() -> None:
    assert registry.filters(FileFormat.MCSB) == {".mcsb"}
    assert {".nbt", "itemnames.dat"} <= registry.filters(FileFormat.NBT)


def test_conversions() -> None:
    conversion = registry.conversions[FileFormat.MCSB, FileFormat.GLB]

    assert conversion.decoder is registry.decoders[FileFormat.MCSB]
    assert conversion.encoder is registry.encoders[FileFormat.GLB]
    assert (FileFormat.MCAL, FileFormat.GLB) not in registry.conversions
    assert (FileFormat.LANG, FileFormat.JSON) in registry.conversions
    assert (FileFormat.SIGN, FileFormat.JSON) in registry.conversions
    assert (FileFormat.MAP, FileFormat.JSON) in registry.conversions
