from pathlib import Path

from scfile.file import McsaDecoder, ObjEncoder
from scfile.file.data import ModelData


def test_default(assets: Path, temp_file: str):
    mcsa = McsaDecoder(assets / "model.mcsa")
    data: ModelData = mcsa.decode()
    mcsa.close()

    obj = ObjEncoder(data)
    obj.encode().save(temp_file)


def test_content_bytes(assets: Path, temp_file: str):
    mcsa = McsaDecoder(assets / "model.mcsa")
    data: ModelData = mcsa.decode()
    mcsa.close()

    obj = ObjEncoder(data)
    obj.encode()

    with open(temp_file, "wb") as fp:
        fp.write(obj.content)

    obj.close()


def test_sugar_convert_to(assets: Path, temp_file: str):
    mcsa = McsaDecoder(assets / "model.mcsa")
    mcsa.convert_to(ObjEncoder).save(temp_file)
    mcsa.close()


def test_sugar_to_xxx(assets: Path, temp_file: str):
    mcsa = McsaDecoder(assets / "model.mcsa")
    mcsa.to_obj().save(temp_file)
    mcsa.close()


def test_context_manager(assets: Path, temp_file: str):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        data: ModelData = mcsa.decode()

    with ObjEncoder(data) as obj:
        obj.encode().save(temp_file)


def test_context_manager_convert_to(assets: Path, temp_file: str):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        obj = mcsa.convert_to(ObjEncoder)
        obj.close()


def test_context_manager_to_xxx(assets: Path, temp_file: str):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        mcsa.to_obj().save(temp_file)
