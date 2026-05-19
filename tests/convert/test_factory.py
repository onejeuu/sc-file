from pathlib import Path

from scfile.convert.factory import _REGISTRY, converter, converters, registry
from scfile.enums import FileFormat
from tests.conftest import FakeDecoder, FakeEncoder


def test_converter_registers():
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    reg = registry()
    assert FileFormat.MCSA in reg
    assert FileFormat.OBJ in reg[FileFormat.MCSA]

    _REGISTRY.clear()


def test_converters_copy():
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    result = converters("mcsa")
    result["glb"] = lambda: None
    assert "glb" not in _REGISTRY["mcsa"]

    _REGISTRY.clear()


def test_converters_strips_dot():
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    assert converters(".mcsa") == converters("mcsa")

    _REGISTRY.clear()


def test_converter_calls_convert(temp: Path):
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    fake_convert(src)
    assert (temp / "model.obj").exists()

    _REGISTRY.clear()
