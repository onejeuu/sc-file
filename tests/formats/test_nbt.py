from pathlib import Path

from scfile.formats.json import JsonEncoder
from scfile.formats.nbt import NbtDecoder

from .conftest import extract


def test_nbt(assets: Path):
    source, output = extract(NbtDecoder, JsonEncoder, assets, "nbt", "nbt")
    assert source == output


def test_gzip(assets: Path):
    source, output = extract(NbtDecoder, JsonEncoder, assets, "nbt_gzip", "nbt")
    assert source == output


def test_zstd(assets: Path):
    source, output = extract(NbtDecoder, JsonEncoder, assets, "nbt_zstd", "nbt")
    assert source == output
