import struct

import numpy as np

from scfile.content.regions import ChunkHeader
from scfile.formats.mdat.payload import BIOME_SIZE, NIBBLE_SIZE, SECTION_SIZE, chunk


def test_block_planes_are_available_without_extended_chunk():
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


def test_records_remain_extended_data():
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
    kind=0,
    x=-1,
    y=67,
    z=16,
    flags=0x7F,
    main=0xD123,
):
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


def _chunk_with_records(record_data: bytes, *, add_mask=1 << 4, extended=False):
    blocks = bytes([0xC2]) * SECTION_SIZE
    metadata = bytes([0xAA]) * NIBBLE_SIZE
    lighting = bytes(NIBBLE_SIZE * 3)
    additions = bytes([0x99]) * NIBBLE_SIZE if add_mask else b""
    biomes = bytes(BIOME_SIZE)
    raw = blocks + metadata + lighting + additions + biomes + record_data
    header = ChunkHeader(0, 1 << 4, add_mask, len(raw), 0)
    return chunk(0, header, raw, extended=extended)


def test_tile_primary_materials_are_decoded_without_exposing_extended_records():
    record_data = struct.pack(">i", 1) + _tile_record(kind=1)
    result = _chunk_with_records(record_data, extended=False)

    assert result.records is None
    assert result.materials is not None
    assert len(result.materials.positions) == 12
    assert len(result.materials.states) == 2
    assert bytes(result.sections[0].blocks) == bytes([0xC2]) * SECTION_SIZE
    assert bytes(result.sections[0].metadata) == bytes([0xAA]) * NIBBLE_SIZE

    position = np.frombuffer(result.materials.positions, dtype=">i4")
    state = np.frombuffer(result.materials.states, dtype=">u2")
    assert tuple(position) == (-1, 67, 16)
    assert state[0] == 0xD123


def test_primary_material_is_the_only_state_retained_from_each_record():
    record_data = struct.pack(">i", 1) + _tile_record(flags=0, main=0)
    result = _chunk_with_records(record_data, add_mask=0)

    assert result.materials is not None
    assert np.frombuffer(result.materials.states, dtype=">u2")[0] == 0


def test_extended_records_are_retained_alongside_compact_materials():
    record_data = struct.pack(">i", 1) + _tile_record(kind=1)
    result = _chunk_with_records(record_data, extended=True)

    assert result.records is not None
    assert result.records.count == 1
    assert len(result.records.records) == 1
    assert result.records.records[0].covers[-1] & 0xFFFF == 0xD123
    assert result.materials is not None


def test_malformed_records_do_not_produce_partial_material_projection():
    terrain = bytes(SECTION_SIZE + NIBBLE_SIZE * 4 + BIOME_SIZE)
    raw = terrain + struct.pack(">i", 1) + _tile_record()[:-1]
    header = ChunkHeader(0, 1, 0, len(raw), 0)

    result = chunk(0, header, raw, extended=False)

    assert result.materials is None
