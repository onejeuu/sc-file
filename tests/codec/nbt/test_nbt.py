from pathlib import Path

from scfile.formats.json.encoder import JsonEncoder
from scfile.formats.nbt.decoder import NbtDecoder
from tests.codec.extract import extract


def test_nbt_to_json(assets: Path):
    converted, expected = extract(NbtDecoder, JsonEncoder, assets, "input")
    assert converted == expected


def test_nbt_gzip_to_json(assets: Path):
    converted, expected = extract(NbtDecoder, JsonEncoder, assets, "input_gzip")
    assert converted == expected


def test_nbt_zstd_to_json(assets: Path):
    converted, expected = extract(NbtDecoder, JsonEncoder, assets, "input_zstd")
    assert converted == expected
