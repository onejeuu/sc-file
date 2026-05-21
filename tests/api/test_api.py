import io
from pathlib import Path

import pytest

from scfile.core import UserOptions
from scfile.exceptions import EmptyFileError, InvalidSignatureError
from tests.conftest import DATA, OUTPUT, SOURCE, FakeContent, FakeDecoder, FakeEncoder


def test_decode_from_bytes():
    dec = FakeDecoder(DATA)
    assert dec.decode().parsed == DATA


def test_decode_from_path(temp: Path):
    (temp / SOURCE).write_bytes(DATA)
    dec = FakeDecoder(temp / SOURCE)
    assert dec.decode().parsed == DATA


def test_decode_from_bytesio():
    dec = FakeDecoder(io.BytesIO(DATA))
    assert dec.decode().parsed == DATA


def test_decode_from_open_file(temp: Path):
    (temp / SOURCE).write_bytes(DATA)
    with open(temp / SOURCE, "rb") as fp:
        dec = FakeDecoder(fp)
        assert dec.decode().parsed == DATA


def test_decode_with_options():
    dec = FakeDecoder(DATA, options=UserOptions(parse_skeleton=True))
    assert dec.options.parse_skeleton is True
    dec.decode()


def test_decode_seek(temp: Path):
    (temp / SOURCE).write_bytes(DATA)
    dec = FakeDecoder(temp / SOURCE)
    dec.decode(seek=True)
    assert dec.tell() == 0


def test_decode_no_seek(temp: Path):
    (temp / SOURCE).write_bytes(DATA)
    dec = FakeDecoder(temp / SOURCE)
    dec.decode(seek=False)
    assert dec.tell() == len(DATA)


def test_context_manager_decoder(temp: Path):
    (temp / SOURCE).write_bytes(DATA)
    with FakeDecoder(temp / SOURCE) as dec:
        assert dec.decode().parsed == DATA
    assert dec.closed


def test_convert_to():
    dec = FakeDecoder(DATA)
    enc = dec.convert_to(FakeEncoder)
    assert enc.getvalue() == DATA
    enc.close()


def test_convert_to_with_options():
    dec = FakeDecoder(DATA)
    enc = dec.convert_to(FakeEncoder, options=UserOptions(on_conflict="rename"))
    assert enc.options.on_conflict == "rename"
    enc.close()


def test_convert():
    dec = FakeDecoder(DATA)
    assert dec.convert(FakeEncoder) == DATA


def test_convert_with_options():
    dec = FakeDecoder(DATA)
    result = dec.convert(FakeEncoder, options=UserOptions(on_conflict="skip"))
    assert result == DATA


def test_encode_default():
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    assert enc.getvalue() == DATA


def test_encode_to_file(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA), output=temp / OUTPUT)
    enc.encode()
    enc.close()
    assert (temp / OUTPUT).read_bytes() == DATA


def test_encode_to_bytesio():
    buf = io.BytesIO()
    enc = FakeEncoder(FakeContent(parsed=DATA), output=buf)
    enc.encode()
    result = buf.getvalue()
    enc.close()
    assert result == DATA


def test_save(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode().save(temp / OUTPUT)
    assert (temp / OUTPUT).read_bytes() == DATA
    assert enc.closed


def test_save_as_multiple(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    enc.save_as(temp / f"a_{OUTPUT}")
    enc.save_as(temp / f"b_{OUTPUT}")
    enc.close()
    assert (temp / f"a_{OUTPUT}").read_bytes() == DATA
    assert (temp / f"b_{OUTPUT}").read_bytes() == DATA


def test_export(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode().export(temp / "file")
    assert (temp / "file.obj").read_bytes() == DATA
    assert enc.closed


def test_export_as(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode().export_as(temp / "file")
    assert (temp / "file.obj").read_bytes() == DATA


def test_chain_decode_encode_save(temp: Path):
    dec = FakeDecoder(DATA)
    enc = dec.convert_to(FakeEncoder)
    enc.save(temp / OUTPUT)
    assert (temp / OUTPUT).read_bytes() == DATA


def test_chain_context_manager(temp: Path):
    (temp / SOURCE).write_bytes(DATA)
    with FakeDecoder(temp / SOURCE) as dec:
        with dec.convert_to(FakeEncoder) as enc:
            enc.save(temp / OUTPUT)
    assert (temp / OUTPUT).read_bytes() == DATA


def test_empty_file_error():
    with pytest.raises(EmptyFileError):
        FakeDecoder(b"").decode()


def test_wrong_signature_error():
    class _Dec(FakeDecoder):
        signature = b"STRN"

    with pytest.raises(InvalidSignatureError):
        _Dec(b"HXGNdata").decode()


def test_no_signature():
    class _Dec(FakeDecoder):
        signature = None

    assert _Dec(DATA).decode().parsed == DATA


def test_closed_after_context():
    with FakeDecoder(DATA) as dec:
        dec.decode()
    assert dec.closed


def test_closed_after_manual():
    dec = FakeDecoder(DATA)
    dec.decode()
    dec.close()
    assert dec.closed
