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
