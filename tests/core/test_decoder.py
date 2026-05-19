import pytest

from scfile.core.options import UserOptions
from scfile.exceptions import EmptyFileError, InvalidSignatureError

from .conftest import FakeDecoder, FakeEncoder


def test_decode_parses_data():
    dec = FakeDecoder(b"STRNhello")
    data = dec.decode()
    assert data.parsed == b"hello"
    dec.close()


def test_decode_with_seek():
    dec = FakeDecoder(b"STRNworld")
    data = dec.decode(seek=True)
    assert data.parsed == b"world"
    assert dec.tell() == 0
    dec.close()


def test_decode_without_seek():
    data = b"STRNworld"
    dec = FakeDecoder(data)
    dec.decode(seek=False)
    assert dec.tell() == len(data)
    dec.close()


def test_decode_empty():
    dec = FakeDecoder(b"")
    with pytest.raises(EmptyFileError):
        dec.decode()
    dec.close()


def test_decode_wrong_signature():
    dec = FakeDecoder(b"XXXX....")
    with pytest.raises(InvalidSignatureError):
        dec.decode()
    dec.close()


def test_decode_no_signature():
    class _NoSig(FakeDecoder):
        signature = None

    dec = _NoSig(b"rawdata")
    data = dec.decode()
    assert data.parsed == b"rawdata"
    dec.close()


def test_prelude_order():
    log = []

    class _Prelude(FakeDecoder):
        def prelude(self):
            log.append("pre")

        def parse(self):
            log.append("parse")
            super().parse()

    dec = _Prelude(b"STRNdata")
    dec.decode()
    assert log == ["pre", "parse"]
    dec.close()


def test_convert_to():
    dec = FakeDecoder(b"STRNpayload")
    enc = dec.convert_to(FakeEncoder)
    assert enc.getvalue() == b"HXGNpayload"
    assert enc.data.parsed == b"payload"
    enc.close()
    dec.close()


def test_convert_to_options():
    dec = FakeDecoder(b"STRNx")
    enc = dec.convert_to(FakeEncoder, options=UserOptions(on_conflict="skip"))
    assert enc.options.on_conflict == "skip"
    enc.close()
    dec.close()


def test_convert():
    dec = FakeDecoder(b"STRNbytes")
    result = dec.convert(FakeEncoder)
    assert result == b"HXGNbytes"
    dec.close()


def test_context_manager():
    with FakeDecoder(b"STRNtest") as dec:
        data = dec.decode()
        assert data.parsed == b"test"
    assert dec.closed
