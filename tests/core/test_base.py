import io
from pathlib import Path

import pytest

from scfile.core.base import BaseFile
from scfile.enums import FileFormat
from scfile.exceptions import InvalidStructureError


class _TestFile(BaseFile):
    format = FileFormat.OBJ


def test_from_path(temp: Path):
    path = temp / "test.bin"
    path.write_bytes(b"hello")
    f = _TestFile(path, mode="rb")
    assert f.read() == b"hello"
    assert not f.closed
    f.close()
    assert f.closed


def test_from_bytes():
    f = _TestFile(b"hello", mode="rb")
    assert f.read() == b"hello"
    f.close()


def test_from_bytesio():
    buf = io.BytesIO(b"hello")
    f = _TestFile(buf, mode="rb")
    assert f.read() == b"hello"
    f.close()


def test_from_file_object(temp: Path):
    path = temp / "test.bin"
    path.write_bytes(b"hello")
    with open(path, "rb") as fh:
        f = _TestFile(fh, mode="rb")
        assert f.read() == b"hello"
        f.close()


def test_invalid_stream_type():
    with pytest.raises(TypeError):
        _TestFile(73, mode="rb")  # type: ignore[arg-type]


def test_write_mode(temp: Path):
    path = temp / "out.bin"
    f = _TestFile(path, mode="wb")
    f.write(b"data")
    f.close()
    assert path.read_bytes() == b"data"


def test_getvalue_bytesio():
    f = _TestFile(b"hello", mode="rb")
    assert f.getvalue() == b"hello"


def test_getvalue_file(temp: Path):
    path = temp / "out.bin"
    f = _TestFile(path, mode="wb+")
    f.write(b"data")
    assert f.getvalue() == b"data"
    f.close()


def test_location_path(temp: Path):
    path = temp / "loc.bin"
    f = _TestFile(path, mode="wb")
    assert "loc.bin" in f.location
    f.close()


def test_location_bytesio():
    f = _TestFile(b"data", mode="rb")
    assert "BytesIO" in f.location
    f.close()


def test_size_bytesio():
    f = _TestFile(b"hello", mode="rb")
    assert f.size == 5


def test_size_file(temp: Path):
    path = temp / "size.bin"
    path.write_bytes(b"1234567")
    f = _TestFile(path, mode="rb")
    assert f.size == 7
    f.close()


def test_is_eof():
    f = _TestFile(b"ab", mode="rb")
    assert not f.is_eof()
    f.read(1)
    assert not f.is_eof()
    f.read(1)
    assert f.is_eof()


def test_context_manager(temp: Path):
    path = temp / "ctx.bin"
    path.write_bytes(b"test")
    with _TestFile(path, mode="rb") as f:
        assert f.read() == b"test"
    assert f.closed


def test_readable():
    f = _TestFile(b"data", mode="rb")
    assert f.readable()
    f.close()


def test_writable():
    f = _TestFile(b"", mode="wb")
    assert f.writable()
    f.close()


def test_seekable():
    f = _TestFile(b"data", mode="rb")
    assert f.seekable()
    f.close()


def test_flush():
    f = _TestFile(b"data", mode="wb")
    f.flush()
    f.close()


def test_tell_and_seek():
    f = _TestFile(b"hello", mode="rb")
    assert f.tell() == 0
    f.seek(2)
    assert f.tell() == 2
    assert f.read() == b"llo"
    f.close()


def test_getvalue(temp: Path):
    path = temp / "out.bin"
    f = _TestFile(path, mode="wb+")
    f.write(b"data")
    result = f.getvalue()
    assert result == b"data"
    assert f.tell() == len(result)
    f.close()


def test_unpack_error(temp: Path):
    path = temp / "bad.bin"
    path.write_bytes(b"\x00")
    f = _TestFile(path, mode="rb")
    with pytest.raises(InvalidStructureError):
        f._unpack("i")
    f.close()


def test_repr():
    f = _TestFile(b"data", mode="rb")
    assert isinstance(repr(f), str)
    f.close()
