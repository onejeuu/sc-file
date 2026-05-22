from io import BytesIO

import numpy as np
import pytest

from scfile.formats.fbx.enums import PropertyType as Prop
from scfile.formats.fbx.io import FbxFileIO


class _TestIO(FbxFileIO, BytesIO):
    pass


@pytest.fixture
def io():
    return _TestIO()


def test_write_bool_true(io: _TestIO):
    io._write_bool(True)
    io.seek(0)
    assert io.read(1) == bytes([Prop.BOOL])
    assert io.read(1) == b"\x01"


def test_write_bool_false(io: _TestIO):
    io._write_bool(False)
    io.seek(0)
    assert io.read(1) == bytes([Prop.BOOL])
    assert io.read(1) == b"\x00"


def test_write_int32(io: _TestIO):
    io._write_int32(42)
    io.seek(0)
    assert io.read(1) == bytes([Prop.INT32])
    assert io.read(4) == (42).to_bytes(4, "little", signed=True)


def test_write_int64(io: _TestIO):
    io._write_int64(np.int64(99))
    io.seek(0)
    assert io.read(1) == bytes([Prop.INT64])
    assert io.read(8) == (99).to_bytes(8, "little", signed=True)


def test_write_double_float(io: _TestIO):
    io._write_double(3.14)
    io.seek(0)
    assert io.read(1) == bytes([Prop.DOUBLE])


def test_write_double_np(io: _TestIO):
    io._write_double(np.float32(2.72))
    io.seek(0)
    assert io.read(1) == bytes([Prop.DOUBLE])


def test_write_string_str(io: _TestIO):
    io._write_string("abc")
    io.seek(0)
    assert io.read(1) == bytes([Prop.STRING])
    assert io.read(4) == (3).to_bytes(4, "little")
    assert io.read(3) == b"abc"


def test_write_string_bytes(io: _TestIO):
    io._write_string(b"xyz")
    io.seek(0)
    assert io.read(1) == bytes([Prop.STRING])
    assert io.read(4) == (3).to_bytes(4, "little")
    assert io.read(3) == b"xyz"


def test_write_array_float32(io: _TestIO):
    arr = np.array([1.0, 2.0], dtype=np.float32)
    io._write_array(arr)
    io.seek(0)
    assert io.read(1) == bytes([Prop.ARRAY_FLOAT])
    assert io.read(4) == (2).to_bytes(4, "little")
    assert io.read(4) == (0).to_bytes(4, "little")
    assert io.read(4) == (8).to_bytes(4, "little")
    assert io.read(8) == arr.tobytes()


def test_write_array_float64(io: _TestIO):
    arr = np.array([1.0, 2.0], dtype=np.float64)
    io._write_array(arr)
    io.seek(0)
    assert io.read(1) == bytes([Prop.ARRAY_DOUBLE])
    assert io.read(4) == (2).to_bytes(4, "little")
    assert io.read(4) == (0).to_bytes(4, "little")
    assert io.read(4) == (16).to_bytes(4, "little")
    assert io.read(16) == arr.tobytes()


def test_write_array_int32(io: _TestIO):
    arr = np.array([1, 2], dtype=np.int32)
    io._write_array(arr)
    io.seek(0)
    assert io.read(1) == bytes([Prop.ARRAY_INT32])
    assert io.read(4) == (2).to_bytes(4, "little")
    assert io.read(4) == (0).to_bytes(4, "little")
    assert io.read(4) == (8).to_bytes(4, "little")
    assert io.read(8) == arr.tobytes()


def test_write_array_int64(io: _TestIO):
    arr = np.array([1, 2], dtype=np.int64)
    io._write_array(arr)
    io.seek(0)
    assert io.read(1) == bytes([Prop.ARRAY_INT64])
    assert io.read(4) == (2).to_bytes(4, "little")
    assert io.read(4) == (0).to_bytes(4, "little")
    assert io.read(4) == (16).to_bytes(4, "little")
    assert io.read(16) == arr.tobytes()


def test_write_property_bool(io: _TestIO):
    io._write_property(True)
    io.seek(0)
    assert io.read(1) == bytes([Prop.BOOL])


def test_write_property_int(io: _TestIO):
    io._write_property(42)
    io.seek(0)
    assert io.read(1) == bytes([Prop.INT32])


def test_write_property_np_int(io: _TestIO):
    io._write_property(np.int64(99))
    io.seek(0)
    assert io.read(1) == bytes([Prop.INT64])


def test_write_property_float(io: _TestIO):
    io._write_property(3.14)
    io.seek(0)
    assert io.read(1) == bytes([Prop.DOUBLE])


def test_write_property_str(io: _TestIO):
    io._write_property("abc")
    io.seek(0)
    assert io.read(1) == bytes([Prop.STRING])


def test_write_property_list(io: _TestIO):
    io._write_property([1.0, 2.0])
    io.seek(0)
    assert io.read(1) == bytes([Prop.ARRAY_DOUBLE])


def test_write_property_array(io: _TestIO):
    io._write_property(np.array([1.0, 2.0], dtype=np.float32))
    io.seek(0)
    assert io.read(1) == bytes([Prop.ARRAY_FLOAT])
