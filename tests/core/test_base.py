import io
from pathlib import Path

import pytest

from scfile.core.base import BaseFile
from scfile.enums import FileFormat
from scfile.exceptions import InvalidStructureError
from tests.conftest import DATA, OUTPUT, SOURCE


class _TestFile(BaseFile):
    format = FileFormat.NONE


def test_from_path(temp: Path):
    path = temp / SOURCE
    path.write_bytes(DATA)
    f = _TestFile(path, mode="rb")
    assert f.read() == DATA
    assert not f.closed
    f.close()
    assert f.closed


def test_from_bytes():
    f = _TestFile(DATA, mode="rb")
    assert f.read() == DATA
    f.close()


def test_from_bytesio():
    buf = io.BytesIO(DATA)
    f = _TestFile(buf, mode="rb")
    assert f.read() == DATA
    f.close()


def test_from_file_object(temp: Path):
    path = temp / SOURCE
    path.write_bytes(DATA)
    with open(path, "rb") as fh:
        f = _TestFile(fh, mode="rb")
        assert f.read() == DATA
        f.close()


def test_invalid_stream_type():
    with pytest.raises(TypeError):
        _TestFile(73, mode="rb")  # type: ignore[arg-type]


def test_write_mode(temp: Path):
    path = temp / OUTPUT
    f = _TestFile(path, mode="wb")
    f.write(DATA)
    f.close()
    assert path.read_bytes() == DATA


def test_getvalue_bytesio():
    f = _TestFile(DATA, mode="rb")
    assert f.getvalue() == DATA


def test_getvalue_file(temp: Path):
    path = temp / OUTPUT
    f = _TestFile(path, mode="wb+")
    f.write(DATA)
    assert f.getvalue() == DATA
    f.close()


def test_location_path(temp: Path):
    path = temp / "location.bin"
    f = _TestFile(path, mode="wb")
    assert "location.bin" in f.location
    f.close()


def test_location_bytesio():
    f = _TestFile(DATA, mode="rb")
    assert "BytesIO" in f.location
    f.close()


def test_size_bytesio():
    f = _TestFile(DATA, mode="rb")
    assert f.size() == len(DATA)


def test_size_file(temp: Path):
    path = temp / SOURCE
    path.write_bytes(DATA)
    f = _TestFile(path, mode="rb")
    assert f.size() == len(DATA)
    f.close()


def test_is_eof():
    f = _TestFile(DATA, mode="rb")
    assert not f.is_eof()
    f.read(len(DATA) // 2)
    assert not f.is_eof()
    f.read()
    assert f.is_eof()


def test_context_manager(temp: Path):
    path = temp / SOURCE
    path.write_bytes(DATA)
    with _TestFile(path, mode="rb") as f:
        assert f.read() == DATA
    assert f.closed


def test_readable():
    f = _TestFile(DATA, mode="rb")
    assert f.readable()
    f.close()


def test_writable():
    f = _TestFile(b"", mode="wb")
    assert f.writable()
    f.close()


def test_seekable():
    f = _TestFile(DATA, mode="rb")
    assert f.seekable()
    f.close()


def test_flush():
    f = _TestFile(DATA, mode="wb")
    f.flush()
    f.close()


def test_getvalue(temp: Path):
    path = temp / OUTPUT
    f = _TestFile(path, mode="wb+")
    f.write(DATA)
    result = f.getvalue()
    assert result == DATA
    assert f.tell() == len(result)
    f.close()


def test_unpack_error(temp: Path):
    path = temp / SOURCE
    path.write_bytes(b"\x00")
    f = _TestFile(path, mode="rb")
    with pytest.raises(InvalidStructureError):
        f._unpack("i")
    f.close()


def test_repr():
    f = _TestFile(DATA, mode="rb")
    assert isinstance(repr(f), str)
    f.close()
