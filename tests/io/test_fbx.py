import struct
from io import BytesIO

import numpy as np
import pytest

from scfile.formats.fbx.enums import PropertyType as Prop
from scfile.io.fbx import FbxWriter, Value


@pytest.mark.parametrize(
    ("value", "tag", "payload"),
    (
        (True, Prop.BOOL, b"\x01"),
        (42, Prop.INT32, struct.pack("<i", 42)),
        (np.int64(42), Prop.INT64, struct.pack("<q", 42)),
        (1.5, Prop.DOUBLE, struct.pack("<d", 1.5)),
        ("text", Prop.STRING, struct.pack("<I", 4) + b"text"),
        (b"text", Prop.STRING, struct.pack("<I", 4) + b"text"),
    ),
)
def test_property(value: Value, tag: Prop, payload: bytes) -> None:
    with FbxWriter(BytesIO()) as writer:
        writer.property(value)

        assert writer.to_bytes() == bytes((tag,)) + payload


@pytest.mark.parametrize(
    ("values", "tag"),
    (
        (np.array([1.0, 2.0], dtype=np.float32), Prop.ARRAY_FLOAT),
        (np.array([1.0, 2.0], dtype=np.float64), Prop.ARRAY_DOUBLE),
        (np.array([1, 2], dtype=np.int32), Prop.ARRAY_INT32),
        (np.array([1, 2], dtype=np.int64), Prop.ARRAY_INT64),
    ),
)
def test_array(values: np.ndarray, tag: Prop) -> None:
    with FbxWriter(BytesIO()) as writer:
        writer.property(values)
        data = writer.to_bytes()

    assert data[0] == tag
    assert struct.unpack("<III", data[1:13]) == (len(values), 0, values.nbytes)
    assert data[13:] == values.tobytes()


def test_list() -> None:
    with FbxWriter(BytesIO()) as writer:
        writer.property([1, 2])
        data = writer.to_bytes()

    assert data[0] == Prop.ARRAY_DOUBLE
    assert struct.unpack("<III", data[1:13]) == (2, 0, 16)
