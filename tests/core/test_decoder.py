from dataclasses import dataclass, field

import pytest

from scfile.core.content import FileContent
from scfile.core.decoder import FileDecoder
from scfile.core.encoder import FileEncoder
from scfile.core.options import UserOptions
from scfile.enums import FileFormat, FileType
from scfile.exceptions import EmptyFileError, InvalidSignatureError


@dataclass
class _TestContent(FileContent):
    type: FileType = field(default=FileType.NONE)
    parsed: bytes = field(default_factory=bytes)


class _TestDecoder(FileDecoder[_TestContent]):
    format = FileFormat.NONE
    signature = b"STRN"
    _content = _TestContent

    def parse(self) -> None:
        self.data.parsed = self.read()


class _TestEncoder(FileEncoder[_TestContent]):
    format = FileFormat.NONE
    signature = b"HXGN"

    def serialize(self) -> None:
        self.write(self.data.parsed)


def test_decode_parses_data():
    dec = _TestDecoder(b"STRNhello")
    data = dec.decode()
    assert data.parsed == b"hello"
    dec.close()


def test_decode_with_seek():
    dec = _TestDecoder(b"STRNworld")
    data = dec.decode(seek=True)
    assert data.parsed == b"world"
    assert dec.tell() == 0
    dec.close()


def test_decode_without_seek():
    data = b"STRNworld"
    dec = _TestDecoder(data)
    dec.decode(seek=False)
    assert dec.tell() == len(data)
    dec.close()


def test_decode_empty():
    dec = _TestDecoder(b"")
    with pytest.raises(EmptyFileError):
        dec.decode()
    dec.close()


def test_decode_wrong_signature():
    dec = _TestDecoder(b"XXXX....")
    with pytest.raises(InvalidSignatureError):
        dec.decode()
    dec.close()


def test_decode_no_signature():
    class _NoSig(_TestDecoder):
        signature = None

    dec = _NoSig(b"rawdata")
    data = dec.decode()
    assert data.parsed == b"rawdata"
    dec.close()


def test_prelude_order():
    log = []

    class _Prelude(_TestDecoder):
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
    dec = _TestDecoder(b"STRNpayload")
    enc = dec.convert_to(_TestEncoder)
    assert enc.getvalue() == b"HXGNpayload"
    assert enc.data.parsed == b"payload"
    enc.close()
    dec.close()


def test_convert_to_options():
    dec = _TestDecoder(b"STRNx")
    enc = dec.convert_to(_TestEncoder, options=UserOptions(on_conflict="skip"))
    assert enc.options.on_conflict == "skip"
    enc.close()
    dec.close()


def test_convert():
    dec = _TestDecoder(b"STRNbytes")
    result = dec.convert(_TestEncoder)
    assert result == b"HXGNbytes"
    dec.close()


def test_context_manager():
    with _TestDecoder(b"STRNtest") as dec:
        data = dec.decode()
        assert data.parsed == b"test"
    assert dec.closed
