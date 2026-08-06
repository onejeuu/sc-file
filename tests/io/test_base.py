from io import BytesIO, IOBase, StringIO
from pathlib import Path

import numpy as np
import pytest

from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError, SafetyLimitError
from scfile.io import StructReader, StructWriter


@pytest.mark.parametrize(
    ("order", "raw"),
    (
        (ByteOrder.LITTLE, b"\x01\x00\x00\x00"),
        (ByteOrder.BIG, b"\x00\x00\x00\x01"),
    ),
)
def test_order(order: ByteOrder, raw: bytes) -> None:
    with StructReader(raw, order=order) as reader:
        assert reader.value(F.I32) == 1


def test_array() -> None:
    with StructReader(b"\x01\x00\x02\x00\x03\x00") as reader:
        values = reader.array(F.I16, 3)

    assert np.array_equal(values, [1, 2, 3])


def test_string() -> None:
    with StructReader(b"\x05\x00hello") as reader:
        assert reader.string() == "hello"


def test_partial_read() -> None:
    with StructReader(b"ab") as reader:
        assert reader.read(4) == b"ab"


def test_skip() -> None:
    with StructReader(b"abc") as reader:
        reader.skip(2)

        assert reader.read() == b"c"
        assert reader.eof()


def test_exact_read() -> None:
    with StructReader(b"ab") as reader:
        with pytest.raises(BinaryStructureError):
            reader.read_exact(4)


def test_signed_count() -> None:
    with StructReader(b"\xff\xff\xff\xff") as reader:
        assert reader.count(F.I32, 10) == -1


def test_limit() -> None:
    with StructReader(b"\x0b\x00\x00\x00") as reader:
        with pytest.raises(SafetyLimitError):
            reader.count(F.U32, 10)


def test_output() -> None:
    output = BytesIO()
    writer = StructWriter(output)
    writer.value(F.I16, 42)

    assert writer.to_bytes() == b"*\x00"
    writer.close()


def test_path_output(tmp_path: Path) -> None:
    path = tmp_path / "output.bin"

    with StructWriter(path) as writer:
        writer.write(b"data")

        assert writer.to_bytes() == b"data"


@pytest.mark.parametrize("stream", (StringIO(), IOBase()))
def test_stream(stream: IOBase) -> None:
    with pytest.raises(TypeError):
        StructReader(stream)  # type: ignore[arg-type]
