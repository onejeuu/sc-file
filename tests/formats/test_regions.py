import struct
import zlib

import numpy as np
import pytest
import zstandard as zstd

from scfile.content.regions import ChunkHeader, RegionChunk
from scfile.content import RegionContent
from scfile.formats.mca import McaEncoder
from scfile.formats.mdat import MdatDecoder
from scfile.formats.mdat.payload import BIOME_SIZE, NIBBLE_SIZE, SECTION_SIZE, chunk
from scfile.options import MdatVersion, Options

from .conftest import ASSETS, export


def _region(version: MdatVersion) -> bytes:
    key_size = 8 if version == 7 else 16
    entry_size = 8 + key_size
    table_size = 1024 * entry_size
    sector = (table_size + 4095) // 4096

    terrain = bytes([42]) * 4096 + bytes(2048 * 4 + 256) + struct.pack(">i", 0)
    compressed = zstd.ZstdCompressor().compress(terrain)

    if version == 7:
        header = struct.pack(">i8s4i", 0, b"ABCDEFGH", 1, 0, len(terrain), len(compressed))
    else:
        header = struct.pack(">5i", 0, 1, 0, len(terrain), len(compressed))

    blob = header + compressed
    if version >= 6:
        objects = zstd.ZstdCompressor().compress(b"\x00")
        blob += struct.pack(">i", len(objects)) + objects

    count = (len(blob) + 4095) // 4096
    table = struct.pack(f">ii{key_size}s", sector, count, b"Z" * key_size)
    table += bytes(table_size - len(table))
    return table + bytes(sector * 4096 - table_size) + blob + bytes(count * 4096 - len(blob))


@pytest.mark.parametrize(
    ("version", "extended", "has_objects"),
    (
        (5, False, False),
        (5, True, False),
        (6, False, False),
        (6, True, True),
        (7, False, False),
        (7, True, True),
    ),
)
def test_mdat_content_and_mca(version: MdatVersion, extended: bool, has_objects: bool) -> None:
    with MdatDecoder(_region(version), options=Options(mdat_version=version, extended_chunk=extended)) as decoder:
        data = decoder.decode()
        assert isinstance(data, RegionContent)
        assert data is decoder.data
        assert len(data.chunks) == 1

        chunk = data.chunks[0]
        assert chunk.index == 0
        assert bytes(chunk.sections[0].blocks) == bytes([42]) * 4096
        assert len(chunk.biomes) == 256
        assert len(chunk.sections[0].metadata) == 2048
        assert (chunk.records is None) is (not extended)
        assert len(chunk.lighting) == 2048 * 3
        assert (chunk.objects is not None) is has_objects
        if chunk.records is not None:
            assert chunk.records.count == 0
        if has_objects:
            assert chunk.objects is not None
            assert chunk.objects.count == 0

        with McaEncoder(data) as encoder:
            assert len(encoder.to_bytes()) >= 8192


def _mca_chunks(data: bytes) -> dict[int, bytes]:
    chunks: dict[int, bytes] = {}

    for index in range(1024):
        location = int.from_bytes(data[index * 4 : index * 4 + 4], "big")
        sector, count = location >> 8, location & 0xFF
        if not sector:
            continue

        start = sector * 4096
        size = struct.unpack(">I", data[start : start + 4])[0]
        assert count > 0
        assert data[start + 4] == 2
        chunks[index] = zlib.decompress(data[start + 5 : start + 4 + size])

    return chunks


def test_mdat_golden_output() -> None:
    root = ASSETS / "region"
    actual = export(MdatDecoder, McaEncoder, root / "source" / "r.0.0.mdat", Options(mdat_version=5))
    expected = (root / "mca" / "r.0.0.mca").read_bytes()

    assert _mca_chunks(actual) == _mca_chunks(expected)


def test_block_planes_are_available_without_extended_chunk() -> None:
    section_mask = 0b11
    add_mask = 0b10
    blocks = bytes([0x11]) * SECTION_SIZE + bytes([0x22]) * SECTION_SIZE
    metadata = bytes([0x33]) * NIBBLE_SIZE + bytes([0x44]) * NIBBLE_SIZE
    lighting = bytes([0x55]) * (NIBBLE_SIZE * 3 * 2)
    additions = bytes([0x66]) * NIBBLE_SIZE
    biomes = bytes([0x77]) * BIOME_SIZE
    raw = blocks + metadata + lighting + additions + biomes
    header = ChunkHeader(0, section_mask, add_mask, len(raw), 0)

    result = chunk(0, header, raw, extended=False)

    assert len(result.sections) == 2
    assert result.sections[0].blocks[0] == 0x11
    assert result.sections[1].blocks[0] == 0x22
    assert result.sections[0].metadata[0] == 0x33
    assert result.sections[1].metadata[0] == 0x44
    assert result.sections[0].additions is None
    assert result.sections[1].additions is not None
    assert result.sections[1].additions[0] == 0x66
    assert len(result.lighting) == len(lighting)
    assert result.lighting[0] == 0x55
    assert result.biomes[0] == 0x77
    assert result.records is None


def test_records_remain_extended_data() -> None:
    section_mask = 0b1
    add_mask = 0
    blocks = bytes(SECTION_SIZE)
    metadata = bytes(NIBBLE_SIZE)
    lighting = bytes(NIBBLE_SIZE * 3)
    biomes = bytes(BIOME_SIZE)
    records = bytes(4)  # zero records
    raw = blocks + metadata + lighting + biomes + records
    header = ChunkHeader(0, section_mask, add_mask, len(raw), 0)

    result = chunk(0, header, raw, extended=True)

    assert result.records is not None
    assert result.records.count == 0


def _tile_record(
    *,
    kind: int = 0,
    x: int = -1,
    y: int = 67,
    z: int = 16,
    flags: int = 0x7F,
    main: int = 0xD123,
) -> bytes:
    covers = (1, 2, 3, 4, 5, 6, main) if flags & 8 else (main,)
    raw = bytearray(struct.pack(">biiiB", kind, x, y, z, flags))
    raw.extend(struct.pack(f">{len(covers)}H", *covers))
    if flags & 2:
        raw.extend(struct.pack(">7h", *range(7)))
    if flags & 4:
        raw.extend(struct.pack(">h", 2))
    if flags & 1:
        raw.extend(struct.pack(">7b", *range(7)))
    if flags & 0x10:
        raw.extend(struct.pack(">h", 3))
    if flags & 0x20:
        raw.extend(struct.pack(">b", 4))
    if flags & 0x40:
        raw.extend(struct.pack(">6b", *range(6)))
    raw.extend(struct.pack(">i", 5))
    if kind == 1:
        raw.extend(struct.pack(">i", 6))
    return bytes(raw)


def _chunk_with_records(
    record_data: bytes,
    *,
    add_mask: int = 1 << 4,
    extended: bool = False,
) -> RegionChunk:
    blocks = bytes([0xC2]) * SECTION_SIZE
    metadata = bytes([0xAA]) * NIBBLE_SIZE
    lighting = bytes(NIBBLE_SIZE * 3)
    additions = bytes([0x99]) * NIBBLE_SIZE if add_mask else b""
    biomes = bytes(BIOME_SIZE)
    raw = blocks + metadata + lighting + additions + biomes + record_data
    header = ChunkHeader(0, 1 << 4, add_mask, len(raw), 0)
    return chunk(0, header, raw, extended=extended)


def test_tile_materials_are_projected_without_records() -> None:
    record_data = struct.pack(">i", 1) + _tile_record(kind=1)
    result = _chunk_with_records(record_data, extended=False)

    assert result.records is None
    assert result.materials is not None
    assert len(result.materials) == 4
    assert bytes(result.sections[0].blocks) == bytes([0xC2]) * SECTION_SIZE
    assert bytes(result.sections[0].metadata) == bytes([0xAA]) * NIBBLE_SIZE

    entry = np.frombuffer(result.materials, dtype=">u4")[0]
    assert entry >> 16 == (4 << 12) | (3 * 256 + 15)
    assert entry & 0xFFFF == 0xD123


def test_tile_materials_keep_primary_state() -> None:
    record_data = struct.pack(">i", 1) + _tile_record(flags=0, main=0)
    result = _chunk_with_records(record_data, add_mask=0)

    assert result.materials is not None
    assert np.frombuffer(result.materials, dtype=">u4")[0] & 0xFFFF == 0


def test_extended_records_keep_compact_materials() -> None:
    record_data = struct.pack(">i", 1) + _tile_record(kind=1)
    result = _chunk_with_records(record_data, extended=True)

    assert result.records is not None
    assert result.records.count == 1
    assert len(result.records.records) == 1
    assert result.records.records[0].covers[-1] & 0xFFFF == 0xD123
    assert result.materials is not None


def test_malformed_records_do_not_project_materials() -> None:
    terrain = bytes(SECTION_SIZE + NIBBLE_SIZE * 4 + BIOME_SIZE)
    raw = terrain + struct.pack(">i", 1) + _tile_record()[:-1]
    header = ChunkHeader(0, 1, 0, len(raw), 0)

    result = chunk(0, header, raw, extended=False)

    assert result.materials is None
