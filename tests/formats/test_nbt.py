from pathlib import Path

from scfile.formats.json import JsonEncoder
from scfile.formats.nbt import NbtDecoder, nbt
from scfile.formats.nbt.enums import Tag

from .conftest import extract


def test_nbt(assets: Path):
    source, output = extract(NbtDecoder, JsonEncoder, assets, "nbt/nbt", "nbt/nbt")
    assert source == output

    source, output = extract(NbtDecoder, JsonEncoder, assets, "nbt/nbt_gzip", "nbt/nbt")
    assert source == output

    source, output = extract(NbtDecoder, JsonEncoder, assets, "nbt/nbt_zstd", "nbt/nbt")
    assert source == output


def test_empty(assets: Path):
    src = assets / "source" / "nbt" / "nbt_empty"
    with NbtDecoder(src) as dec:
        data = dec.decode()
    assert data.value is None


def test_encode():
    output = b"\x03\x00\x04test"
    assert nbt.encode(Tag.INT, b"test") == output


def test_encode_byte():
    output = b"\x01\x00\x01b\x7f"
    assert nbt.encode_byte(b"b", 127) == output


def test_encode_int():
    output = b"\x03\x00\x01i\x00\x00\x00\x2a"
    assert nbt.encode_int(b"i", 42) == output


def test_encode_long():
    output = b"\x04\x00\x01l\x00\x00\x00\x00\x00\x00\x00\x63"
    assert nbt.encode_long(b"l", 99) == output


def test_encode_ba():
    output = b"\x07\x00\x02ba\x00\x00\x00\x03\x01\x02\x03"
    assert nbt.encode_ba(b"ba", b"\x01\x02\x03") == output


def test_encode_ia():
    output = b"\x0b\x00\x02ia\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
    assert nbt.encode_ia(b"ia", (1, 2, 3)) == output


def test_compound():
    inner = nbt.encode_byte(b"x", 1)
    output = b"\x0a\x00\x04root" + inner + b"\x00"
    assert nbt.compound(b"root", inner) == output


def test_lst():
    output = b"\x09\x00\x04list\x03\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02"
    assert nbt.lst(b"list", Tag.INT, b"\x00\x00\x00\x01", b"\x00\x00\x00\x02") == output
