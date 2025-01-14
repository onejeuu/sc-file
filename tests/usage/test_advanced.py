from pathlib import Path

from scfile.core import ModelContext
from scfile.formats.mcsa.decoder import McsaDecoder
from scfile.formats.obj.encoder import ObjEncoder


def test_default(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    data: ModelContext = mcsa.decode()
    mcsa.close()

    obj = ObjEncoder(data)
    obj.encode().save(temp / "model.obj")


def test_content_bytes(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    data: ModelContext = mcsa.decode()
    mcsa.close()

    obj = ObjEncoder(data)
    obj.encode()

    with open(temp / "model.obj", "wb") as fp:
        fp.write(obj.content)

    obj.close()


def test_sugar_convert_to(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    mcsa.convert_to(ObjEncoder).save(temp / "model.obj")
    mcsa.close()


def test_sugar_to_xxx(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    mcsa.to_obj().save(temp / "model.obj")
    mcsa.close()


def test_context_manager(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        data: ModelContext = mcsa.decode()

    with ObjEncoder(data) as obj:
        obj.encode().save(temp / "model.obj")


def test_context_manager_convert_to(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        obj = mcsa.convert_to(ObjEncoder)
        obj.close()


def test_context_manager_to_xxx(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        mcsa.to_obj().save(temp / "model.obj")


def test_context_multiple_copies(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        with mcsa.to_obj() as obj:
            obj.save_as(temp / "model1.obj")
            obj.save_as(temp / "model2.obj")
