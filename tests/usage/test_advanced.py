from pathlib import Path

from scfile.core import ModelContent
from scfile.formats.mcsa.decoder import McsaDecoder
from scfile.formats.obj.encoder import ObjEncoder


def test_default(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    data = mcsa.decode()
    assert isinstance(data, ModelContent)
    mcsa.close()
    assert mcsa.closed

    obj = ObjEncoder(data)
    obj.encode()
    obj.save(temp / "model.obj")
    assert (temp / "model.obj").exists()
    assert (temp / "model.obj").stat().st_size > 0
    assert obj.closed


def test_content_bytes(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")

    data = mcsa.decode()
    assert isinstance(data, ModelContent)

    mcsa.close()
    assert mcsa.closed

    obj = ObjEncoder(data)
    obj.encode()

    with open(temp / "model.obj", "wb") as fp:
        fp.write(obj.getvalue())

    assert (temp / "model.obj").exists()
    assert (temp / "model.obj").stat().st_size > 0

    obj.close()
    assert obj.closed


def test_sugar_convert_to(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    obj = mcsa.convert_to(ObjEncoder)

    assert isinstance(obj.data, ModelContent)
    assert mcsa.data == obj.data

    obj.save(temp / "model.obj")
    assert (temp / "model.obj").exists()
    assert (temp / "model.obj").stat().st_size > 0
    assert obj.closed

    mcsa.close()
    assert mcsa.closed


def test_sugar_to_xxx(assets: Path, temp: Path):
    mcsa = McsaDecoder(assets / "model.mcsa")
    obj = mcsa.to_obj()
    assert isinstance(obj.data, ModelContent)
    assert mcsa.data == obj.data

    obj.save(temp / "model.obj")
    assert (temp / "model.obj").exists()
    assert (temp / "model.obj").stat().st_size > 0
    assert obj.closed

    mcsa.close()
    assert mcsa.closed


def test_context_manager(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        data = mcsa.decode()
        assert isinstance(data, ModelContent)

    assert mcsa.closed

    with ObjEncoder(data) as obj:
        obj.encode().save(temp / "model.obj")

    assert (temp / "model.obj").exists()
    assert (temp / "model.obj").stat().st_size > 0

    assert obj.closed


def test_context_manager_convert_to(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        obj = mcsa.convert_to(ObjEncoder)
        assert not obj.closed

        obj.close()
        assert obj.closed


def test_context_manager_to_xxx(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        obj = mcsa.to_obj()
        obj.save(temp / "model.obj")
        assert (temp / "model.obj").exists()
        assert (temp / "model.obj").stat().st_size > 0
        assert obj.closed

        dae = mcsa.to_dae()
        dae.save(temp / "model.dae")
        assert (temp / "model.dae").exists()
        assert (temp / "model.dae").stat().st_size > 0
        assert dae.closed

    assert mcsa.closed


def test_context_multiple_copies(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        with mcsa.to_obj() as obj:
            obj.save_as(temp / "model1.obj")
            assert not obj.closed

            obj.save_as(temp / "model2.obj")
            assert not obj.closed

            obj.save(temp / "model3.obj")
            assert (temp / "model3.obj").exists()
            assert (temp / "model3.obj").stat().st_size > 0
            assert obj.closed
        assert obj.closed
    assert mcsa.closed


def test_encoded_method(assets: Path, temp: Path):
    with McsaDecoder(assets / "model.mcsa") as mcsa:
        data = mcsa.decode()

    with ObjEncoder(data).encoded() as obj:
        assert obj.getvalue() is not None
        assert len(obj.getvalue()) > 0
        obj.save(temp / "model.obj")

    assert (temp / "model.obj").exists()
    assert (temp / "model.obj").stat().st_size > 0

    assert obj.closed
