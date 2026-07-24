from pathlib import Path

import pytest

from scfile import formats
from scfile.convert.factory import (
    _DECODERS,
    _ENCODERS,
    _REGISTRY,
    converter,
    converters,
    decoders,
    encoders,
    registry,
)
from scfile.enums import FileFormat
from tests.conftest import FakeDecoder, FakeEncoder


@pytest.fixture(autouse=True)
def restore_factory():
    registry_map = registry()
    decoder_map = decoders()
    encoder_map = encoders()
    yield
    _REGISTRY.clear()
    for source, converter_map in registry_map.items():
        _REGISTRY[source].update(converter_map)
    _DECODERS.clear()
    _DECODERS.update(decoder_map)
    _ENCODERS.clear()
    _ENCODERS.update(encoder_map)


def test_converter_registers():
    _DECODERS.pop(FileFormat.MCSA, None)
    _ENCODERS.pop(FileFormat.OBJ, None)

    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    reg = registry()
    assert FileFormat.MCSA in reg
    assert FileFormat.OBJ in reg[FileFormat.MCSA]
    assert decoders()[FileFormat.MCSA] is FakeDecoder
    assert encoders()[FileFormat.OBJ] is FakeEncoder


def test_handlers_registered():
    assert encoders()[FileFormat.DDS] is formats.dds.DdsEncoder


def test_handler_exports():
    assert formats.McsaDecoder is formats.mcsa.McsaDecoder
    assert formats.DaeEncoder is formats.dae.DaeEncoder


def test_handlers_copy():
    decoder_map = decoders()
    encoder_map = encoders()
    decoder_map.clear()
    encoder_map.clear()
    assert _DECODERS
    assert _ENCODERS


def test_converters_copy():
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    result = converters("mcsa")
    result["test"] = lambda: None
    assert "test" not in _REGISTRY["mcsa"]


def test_converters_strips_dot():
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    assert converters(".mcsa") == converters("mcsa")


def test_converter_calls_convert(temp: Path):
    @converter(FakeDecoder, FakeEncoder)
    def fake_convert(source, output=None, options=None):
        pass

    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    fake_convert(src)
    assert (temp / "model.obj").exists()
