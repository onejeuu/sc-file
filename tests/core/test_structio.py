import io

import numpy as np
import pytest

from scfile.core.structio import StructIO
from scfile.enums import ByteOrder, F


class _TestStructIO(StructIO):
    def __init__(self, data: bytes = b""):
        self._buf = io.BytesIO(data)

    def read(self, size: int = -1) -> bytes:
        return self._buf.read(size)

    def write(self, data: bytes) -> int:
        return self._buf.write(data)

    def seek(self, pos: int, whence: int = 0) -> int:
        return self._buf.seek(pos, whence)

    def tell(self) -> int:
        return self._buf.tell()


@pytest.mark.parametrize(
    "fmt, value, raw",
    [
        (F.BOOL, True, b"\x01"),
        (F.I8, -128, b"\x80"),
        (F.I8, 127, b"\x7f"),
        (F.I16, -32768, b"\x00\x80"),
        (F.I16, 32767, b"\xff\x7f"),
        (F.I32, -2147483648, b"\x00\x00\x00\x80"),
        (F.I32, 2147483647, b"\xff\xff\xff\x7f"),
        (F.I64, -9223372036854775808, b"\x00\x00\x00\x00\x00\x00\x00\x80"),
        (F.I64, 9223372036854775807, b"\xff\xff\xff\xff\xff\xff\xff\x7f"),
        (F.U8, 0, b"\x00"),
        (F.U8, 255, b"\xff"),
        (F.U16, 0, b"\x00\x00"),
        (F.U16, 65535, b"\xff\xff"),
        (F.U32, 0, b"\x00\x00\x00\x00"),
        (F.U32, 4294967295, b"\xff\xff\xff\xff"),
        (F.U64, 0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        (F.U64, 18446744073709551615, b"\xff\xff\xff\xff\xff\xff\xff\xff"),
        (F.F16, 1.0, b"\x00\x3c"),
        (F.F16, -2.0, b"\x00\xc0"),
        (F.F32, 1.0, b"\x00\x00\x80\x3f"),
        (F.F32, -2.5, b"\x00\x00\x20\xc0"),
        (F.F64, 1.0, b"\x00\x00\x00\x00\x00\x00\xf0\x3f"),
        (F.F64, -2.5, b"\x00\x00\x00\x00\x00\x00\x04\xc0"),
    ],
)
def test_readb_formats(fmt, value, raw):
    sio = _TestStructIO(raw)
    result = sio._readb(fmt)
    if fmt in (F.F16, F.F32, F.F64):
        assert result == pytest.approx(value, rel=1e-3)
    else:
        assert result == value


@pytest.mark.parametrize(
    "order, raw",
    [
        (ByteOrder.LITTLE, b"\x01\x00\x00\x00"),
        (ByteOrder.BIG, b"\x00\x00\x00\x01"),
        (ByteOrder.NATIVE, b"\x01\x00\x00\x00"),
        (ByteOrder.STANDARD, b"\x01\x00\x00\x00"),
    ],
)
def test_readb_byte_orders(order, raw):
    sio = _TestStructIO(raw)
    assert sio._readb(F.I32, order=order) == 1


@pytest.mark.parametrize(
    "order, raw",
    [
        (ByteOrder.LITTLE, b"\x01\x00\x02\x00\x03\x00"),
        (ByteOrder.BIG, b"\x00\x01\x00\x02\x00\x03"),
    ],
)
def test_readarray_byte_orders(order, raw):
    sio = _TestStructIO(raw)
    arr = sio._readarray(F.I16, 3, order=order)
    assert np.allclose(arr, [1, 2, 3])


def test_readarray_float32():
    sio = _TestStructIO(b"\x00\x00\x80\x3f\x00\x00\x00\x40")
    arr = sio._readarray(F.F32, 2)
    assert np.allclose(arr, [1.0, 2.0])


def test_reads_default():
    sio = _TestStructIO(b"\x05\x00hello")
    assert sio._reads() == b"hello"


@pytest.mark.parametrize(
    "prefix, raw, expected",
    [
        (F.U8, b"\x03abc", b"abc"),
        (F.U16, b"\x03\x00abc", b"abc"),
        (F.I32, b"\x03\x00\x00\x00abc", b"abc"),
    ],
)
def test_reads_prefixes(prefix, raw, expected):
    sio = _TestStructIO(raw)
    assert sio._reads(prefix=prefix) == expected


def test_readutf8():
    sio = _TestStructIO(b"\x0c\x00hello world!")
    assert sio._readutf8() == "hello world!"


def test_writeb_roundtrip():
    sio = _TestStructIO()
    sio._writeb(F.I32, -42)
    sio._buf.seek(0)
    assert sio._readb(F.I32) == -42


def test_writenull_exact():
    sio = _TestStructIO()
    sio._writenull(3)
    assert sio._buf.getvalue() == b"\x00\x00\x00"


def test_writenull_default():
    sio = _TestStructIO()
    sio._writenull()
    assert sio._buf.getvalue() == b"\x00\x00\x00\x00"


def test_writeutf8_roundtrip():
    sio = _TestStructIO()
    sio._writeutf8("test")
    sio._buf.seek(0)
    assert sio._buf.read() == b"test"
