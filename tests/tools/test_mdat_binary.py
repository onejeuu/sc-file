from uuid import UUID

import pytest

from tools.cmd.mapcache.mdat.binary import Reader
from tools.cmd.mapcache.mdat.models import Entry, view


def test_reader_decodes_numbers_vectors_and_uuid() -> None:
    reader = Reader(memoryview(b"\x01\x02\x03\x00\x00\x00\x01" + bytes(range(16))))

    assert reader.number(">B") == 1
    assert reader.numbers("B", 2) == (2, 3)
    assert reader.number(">I") == 1
    assert reader.uuid() == UUID(bytes=bytes(range(16)))


@pytest.mark.parametrize(
    "value, encoded", [(0, b"\x00"), (127, b"\x7f"), (128, b"\x80\x01"), (2**32 - 1, b"\xff\xff\xff\xff\x0f")]
)
def test_varint_boundaries(value: int, encoded: bytes) -> None:
    assert Reader(memoryview(encoded)).varint() == value


def test_varint_rejects_overflow() -> None:
    with pytest.raises(EOFError, match="exceeds"):
        Reader(memoryview(b"\xff\xff\xff\xff\x10")).varint()


@pytest.mark.parametrize("operation", ("skip", "bytes"))
def test_reader_rejects_truncated_data(operation: str) -> None:
    reader = Reader(memoryview(b"abc"))

    with pytest.raises(EOFError):
        getattr(reader, operation)(4)


def test_utf_decodes_modified_nul() -> None:
    raw = b"\x00\x04A\xc0\x80B"

    assert Reader(memoryview(raw)).utf() == "A\0B"


def test_slice_reports_completeness_and_end() -> None:
    complete = view(memoryview(b"abcdef"), 1, 3)
    truncated = view(memoryview(b"ab"), 1, 3)

    assert complete.end == 4
    assert complete.complete
    assert not truncated.complete


def test_entry_uuid_is_none_for_non_uuid_key() -> None:
    entry = Entry(0, 0, 0, b"short", view(memoryview(b""), 0, 0))

    assert entry.uuid is None
