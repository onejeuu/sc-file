from scfile.content import regions as S

from .records import records


SECTION_SIZE = 16 * 16 * 16
NIBBLE_SIZE = SECTION_SIZE // 2

BIOME_SIZE = 16 * 16


def chunk(
    index: int,
    header: S.ChunkHeader,
    data: bytes,
    *,
    objects: bool,
    materials: bool = True,
) -> S.RegionChunk:
    raw = memoryview(data)
    section_ids = [y for y in range(16) if header.section_mask & (1 << y)]

    block_end = len(section_ids) * SECTION_SIZE
    metadata_end = block_end + len(section_ids) * NIBBLE_SIZE
    lighting_end = metadata_end + len(section_ids) * NIBBLE_SIZE * 3
    additions_end = lighting_end + header.add_mask.bit_count() * NIBBLE_SIZE
    biomes_end = additions_end + BIOME_SIZE

    sections: list[S.ChunkSection] = []
    addition_index = 0
    for index_in_data, y in enumerate(section_ids):
        block_offset = index_in_data * SECTION_SIZE
        block_data = raw[block_offset : block_offset + SECTION_SIZE]
        metadata_offset = block_end + index_in_data * NIBBLE_SIZE
        section = S.ChunkSection(
            y=y,
            blocks=block_data,
            metadata=raw[metadata_offset : metadata_offset + NIBBLE_SIZE],
        )

        if header.add_mask & (1 << y):
            addition_offset = lighting_end + addition_index * NIBBLE_SIZE
            section.additions = raw[addition_offset : addition_offset + NIBBLE_SIZE]
            addition_index += 1

        sections.append(section)

    container = S.RegionChunk(
        index=index,
        sections=tuple(sections),
        biomes=raw[additions_end:biomes_end],
        lighting=raw[metadata_end:lighting_end],
    )

    raw_records = raw[biomes_end:]
    if raw_records:
        container.records = S.ChunkRecords(raw=raw_records)

    if (raw_records and materials) or objects:
        decoded_records, tile_materials = records(raw_records, include=objects)
        container.records = decoded_records
        if materials and decoded_records.error is None:
            container.materials = tile_materials

    return container
