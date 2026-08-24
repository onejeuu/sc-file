from scfile.content import regions as S


SECTION_SIZE = 16 * 16 * 16
NIBBLE_SIZE = 16 * 16 * 8
BIOME_SIZE = 16 * 16


def chunk(
    index: int,
    header: S.ChunkHeader,
    data: bytes,
) -> S.RegionChunk:
    raw = memoryview(data)
    section_count = header.section_mask.bit_count()
    add_count = header.add_mask.bit_count()
    block_size = section_count * SECTION_SIZE
    metadata_size = section_count * NIBBLE_SIZE
    lighting_size = metadata_size * 3
    add_size = add_count * NIBBLE_SIZE

    blocks_end = block_size
    metadata_end = blocks_end + metadata_size
    lighting_end = metadata_end + lighting_size
    add_end = lighting_end + add_size
    biomes_end = add_end + BIOME_SIZE

    blocks = raw[:blocks_end]
    metadata = raw[blocks_end:metadata_end]
    additions = raw[lighting_end:add_end]
    sections: list[S.RegionSection] = []

    for section, y in enumerate(y for y in range(16) if (header.section_mask >> y) & 1):
        add_section = (header.add_mask & ((1 << y) - 1)).bit_count()
        add_section_size = NIBBLE_SIZE * ((header.add_mask >> y) & 1)
        sections.append(
            S.RegionSection(
                y=y,
                blocks=blocks[section * SECTION_SIZE : (section + 1) * SECTION_SIZE],
                metadata=metadata[section * NIBBLE_SIZE : (section + 1) * NIBBLE_SIZE],
                additions=additions[
                    add_section * NIBBLE_SIZE : add_section * NIBBLE_SIZE + add_section_size
                ],
            )
        )

    return S.RegionChunk(
        index=index,
        header=header,
        payload=data,
        sections=tuple(sections),
        lighting=raw[metadata_end:lighting_end],
        biomes=raw[add_end:biomes_end],
        records=raw[biomes_end:],
    )
