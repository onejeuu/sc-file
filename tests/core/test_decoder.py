import pytest

from scfile.core.options import UserOptions
from scfile.exceptions import EmptyFileError, InvalidSignatureError
from tests.conftest import DATA, FakeDecoder, FakeEncoder


def test_decode_parses_data():
    dec = FakeDecoder(DATA)
    data = dec.decode()
    assert data.parsed == DATA
    dec.close()


def test_decode_with_seek():
    dec = FakeDecoder(DATA)
    data = dec.decode(seek=True)
    assert data.parsed == DATA
    assert dec.tell() == 0
    dec.close()


def test_decode_without_seek():
    dec = FakeDecoder(DATA)
    dec.decode(seek=False)
    assert dec.tell() == len(DATA)
    dec.close()


def test_decode_empty():
    dec = FakeDecoder(b"")
    with pytest.raises(EmptyFileError):
        dec.decode()
    dec.close()


def test_decode_wrong_signature():
    class _Dec(FakeDecoder):
        signature = b"STRN"

    dec = _Dec(b"HXGNdata")
    with pytest.raises(InvalidSignatureError):
        dec.decode()


def test_decode_no_signature():
    class _Dec(FakeDecoder):
        signature = None

    dec = _Dec(DATA)
    data = dec.decode()
    assert data.parsed == DATA


def test_prelude_order():
    log = []

    class _Prelude(FakeDecoder):
        def prelude(self):
            log.append("pre")

        def parse(self):
            log.append("parse")
            super().parse()

    dec = _Prelude(DATA)
    dec.decode()
    assert log == ["pre", "parse"]
    dec.close()


def test_convert_to():
    dec = FakeDecoder(DATA)
    enc = dec.convert_to(FakeEncoder)
    assert enc.getvalue() == DATA
    assert enc.data.parsed == DATA
    enc.close()
    dec.close()


def test_convert_to_options():
    dec = FakeDecoder(DATA)
    enc = dec.convert_to(FakeEncoder, options=UserOptions(on_conflict="skip"))
    assert enc.options.on_conflict == "skip"
    enc.close()
    dec.close()


def test_convert():
    dec = FakeDecoder(DATA)
    result = dec.convert(FakeEncoder)
    assert result == DATA
    dec.close()


def test_context_manager():
    with FakeDecoder(DATA) as dec:
        data = dec.decode()
        assert data.parsed == DATA
    assert dec.closed
