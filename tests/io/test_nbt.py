import struct
from io import BytesIO

import pytest

from scfile.exceptions import BinaryStructureError
from scfile.io.nbt import NbtReader, NbtWriter, Tag


def test_header() -> None:
    assert Tag.INT.header(b"value") == b"\x03\x00\x05value"


def test_compound() -> None:
    raw = b"\x0a\x00\x00\x03\x00\x01x\x00\x00\x00*\x00"

    with NbtReader(raw) as reader:
        assert reader.document() == {"x": 42}


def test_empty_document() -> None:
    with NbtReader(bytes((Tag.END,))) as reader:
        assert reader.document() is None


@pytest.mark.parametrize(
    ("tag", "raw", "expected"),
    (
        (Tag.BYTE, struct.pack(">b", -1), -1),
        (Tag.SHORT, struct.pack(">h", -2), -2),
        (Tag.INT, struct.pack(">i", -3), -3),
        (Tag.LONG, struct.pack(">q", -4), -4),
        (Tag.FLOAT, struct.pack(">f", 1.5), 1.5),
        (Tag.DOUBLE, struct.pack(">d", 2.5), 2.5),
    ),
)
def test_scalar(tag: Tag, raw: bytes, expected: int | float) -> None:
    with NbtReader(raw) as reader:
        assert reader.parse(tag) == expected


def test_collections() -> None:
    raw = b"".join(
        (
            Tag.COMPOUND.header(),
            Tag.STRING.header(b"text"),
            struct.pack(">H", 2),
            b"ok",
            Tag.LIST.header(b"list"),
            bytes((Tag.INT,)),
            struct.pack(">i", 2),
            struct.pack(">ii", 1, 2),
            Tag.BYTE_ARRAY.header(b"bytes"),
            struct.pack(">i", 2),
            b"\x01\x02",
            Tag.INT_ARRAY.header(b"ints"),
            struct.pack(">iii", 2, 3, 4),
            Tag.LONG_ARRAY.header(b"longs"),
            struct.pack(">iqq", 2, 5, 6),
            bytes((Tag.END,)),
        )
    )

    with NbtReader(raw) as reader:
        assert reader.document() == {
            "text": "ok",
            "list": [1, 2],
            "bytes": b"\x01\x02",
            "ints": [3, 4],
            "longs": [5, 6],
        }


def test_unknown_tag() -> None:
    with NbtReader(b"\x0d") as reader:
        with pytest.raises(BinaryStructureError):
            reader.document()


def test_negative_length() -> None:
    with NbtReader(struct.pack(">i", -1)) as reader:
        with pytest.raises(BinaryStructureError):
            reader.parse(Tag.BYTE_ARRAY)


def test_writer() -> None:
    with NbtWriter(BytesIO()) as writer:
        writer.tag(Tag.COMPOUND)
        writer.list(Tag.INT, 2)
        writer.end()

        assert writer.to_bytes() == b"\x0a\x00\x00\x03\x00\x00\x00\x02\x00"
