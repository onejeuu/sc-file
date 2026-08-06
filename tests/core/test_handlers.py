from dataclasses import replace
from pathlib import Path

import pytest

from scfile.enums import FileFormat, HandlerState
from scfile.exceptions import EmptyFileError, HandlerStateError, SignatureMismatchError
from tests.conftest import BytesDecoder, BytesEncoder, StubContent


class NamedEncoder(BytesEncoder):
    format = FileFormat.PNG


class BrokenEncoder(BytesEncoder):
    def _serialize(self) -> None:
        raise RuntimeError


def test_decoder_decodes_once() -> None:
    decoder = BytesDecoder(b"STRNsource")

    assert decoder.decode().payload == b"source"
    assert decoder.decode() is decoder.data
    assert decoder.state is HandlerState.SUCCEEDED


def test_decoder_rejects_empty_input() -> None:
    decoder = BytesDecoder(b"")

    with pytest.raises(EmptyFileError):
        decoder.decode()

    assert decoder.state is HandlerState.FAILED


def test_decoder_verifies_signature() -> None:
    decoder = BytesDecoder(b"bad")

    with pytest.raises(SignatureMismatchError):
        decoder.decode()

    with pytest.raises(HandlerStateError):
        decoder.decode()


def test_convert_to() -> None:
    with BytesDecoder(b"STRNsource") as decoder:
        encoder = decoder.convert_to(BytesEncoder)

    assert encoder.data.payload == b"source"
    assert encoder.state is HandlerState.INITIAL
    encoder.close()


def test_convert() -> None:
    with BytesDecoder(b"STRNsource") as decoder:
        assert decoder.convert(BytesEncoder) == b"HXGNsource"


def test_encoder_encodes_once() -> None:
    encoder = BytesEncoder(StubContent(payload=b"source"))

    assert encoder.to_bytes() == b"HXGNsource"
    assert encoder.state is HandlerState.SUCCEEDED

    with pytest.raises(HandlerStateError):
        encoder.encode()


def test_save_open(tmp_path: Path) -> None:
    encoder = BytesEncoder(StubContent(payload=b"source"))
    path = tmp_path / "output.bin"

    encoder.save(path, close=False)

    assert path.read_bytes() == b"HXGNsource"
    assert not encoder.closed
    encoder.close()


def test_export(tmp_path: Path) -> None:
    encoder = NamedEncoder(StubContent(payload=b"source"))
    path = tmp_path / "output"

    encoder.export(path)

    assert path.with_suffix(".png").read_bytes() == b"HXGNsource"
    assert encoder.closed


def test_transform() -> None:
    encoder = BytesEncoder(StubContent(payload=b"source"))

    data = encoder.encode(transforms=[lambda content: replace(content, payload=b"transformed")]).data

    assert data.payload == b"transformed"
    assert encoder.to_bytes() == b"HXGNtransformed"


def test_encode_failure() -> None:
    encoder = BrokenEncoder(StubContent())

    with pytest.raises(RuntimeError):
        encoder.encode()

    assert encoder.state is HandlerState.FAILED
    with pytest.raises(HandlerStateError):
        encoder.to_bytes()
    encoder.close()
