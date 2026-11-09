import struct

import numpy as np

from scfile.content.regions import ChunkSection, ChunkTileMaterials, RegionChunk
from scfile.io.nbt import Tag

from .mappings import PRESERVE_METADATA, CompiledBlockMapping


VERSION = Tag.INT.header(b"DataVersion") + struct.pack(">i", 1343)

ROOT = Tag.COMPOUND.header()
LEVEL = Tag.COMPOUND.header(b"Level")
XPOS = Tag.INT.header(b"xPos")
ZPOS = Tag.INT.header(b"zPos")
SECTIONS = Tag.LIST.header(b"Sections")
Y = Tag.BYTE.header(b"Y")
BLOCKS = Tag.BYTE_ARRAY.header(b"Blocks")
DATA = Tag.BYTE_ARRAY.header(b"Data")
BLOCK_LIGHT = Tag.BYTE_ARRAY.header(b"BlockLight")
ADD = Tag.BYTE_ARRAY.header(b"Add")
SKY_LIGHT = Tag.BYTE_ARRAY.header(b"SkyLight")
BIOMES = Tag.BYTE_ARRAY.header(b"Biomes")

Y_VALUES = [struct.pack(">b", y) for y in range(16)]

NIBBLE_SIZE = 16 * 16 * 8

EMPTY_NIBBLES = bytes(NIBBLE_SIZE)
FULL_NIBBLES = b"\xff" * NIBBLE_SIZE


def _array(
    header: bytes,
    data: bytes,
) -> bytes:
    return header + struct.pack(">i", len(data)) + data


def _write_nibbles(plane: np.ndarray, indices: np.ndarray, values: np.ndarray) -> None:
    low = (indices & 1) == 0
    if np.any(low):
        offsets = indices[low] >> 1
        plane[offsets] = (plane[offsets] & 0xF0) | values[low]

    high = ~low
    if np.any(high):
        offsets = indices[high] >> 1
        plane[offsets] = (plane[offsets] & 0x0F) | (values[high] << 4)


def _mapped_low_metadata(
    source_blocks: bytes,
    metadata: np.ndarray,
    mapping: CompiledBlockMapping,
) -> bytes:
    mask = mapping._low_mask
    if mask is None or b"\x01" not in source_blocks.translate(mask):
        return metadata.tobytes()

    source_ids = np.frombuffer(source_blocks, dtype=np.uint8)
    lut = mapping._low_lut
    assert lut is not None

    low = lut[source_ids[::2], metadata & 0x0F]
    high = lut[source_ids[1::2], metadata >> 4]
    return (low | (high << 4)).tobytes()


def _mapped_blocks(
    section: ChunkSection,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
    *,
    tile_indices: np.ndarray | None = None,
    tile_states: np.ndarray | None = None,
) -> tuple[bytes, bytes, bytes]:
    has_tiles = tile_indices is not None and tile_states is not None and len(tile_indices) > 0
    if has_tiles:
        assert tile_indices is not None and tile_states is not None
        indices = tile_indices
        states = tile_states

    if section.additions is None and byte_mapping is not None:
        if not has_tiles:
            source_blocks = bytes(section.blocks)
            blocks = source_blocks.translate(byte_mapping)
            metadata = np.frombuffer(section.metadata, dtype=np.uint8)
            data = _mapped_low_metadata(source_blocks, metadata, mapping)
            return blocks, b"", data

        tile_ids = np.asarray(states & 0x0FFF, dtype=np.uint16) if has_tiles else None
        if tile_ids is not None and not np.any(tile_ids > 0xFF):
            source_ids = np.frombuffer(section.blocks, dtype=np.uint8).copy()
            source_ids[indices] = tile_ids.astype(np.uint8)
            source_blocks = source_ids.tobytes()
            blocks = source_blocks.translate(byte_mapping)

            metadata = np.frombuffer(section.metadata, dtype=np.uint8).copy()
            tile_metadata = np.asarray((states >> 12) & 0x0F, dtype=np.uint8)
            _write_nibbles(metadata, indices, tile_metadata)
            data = _mapped_low_metadata(source_blocks, metadata, mapping)
            return blocks, b"", data

    source_ids = np.frombuffer(section.blocks, dtype=np.uint8).astype(np.uint16)
    if section.additions is not None:
        packed = np.frombuffer(section.additions, dtype=np.uint8)
        source_ids[::2] |= (packed & 0x0F).astype(np.uint16) << 8
        source_ids[1::2] |= (packed >> 4).astype(np.uint16) << 8

    metadata = np.frombuffer(section.metadata, dtype=np.uint8)
    if has_tiles:
        source_ids[indices] = states & 0x0FFF
        metadata = metadata.copy()
        tile_metadata = np.asarray((states >> 12) & 0x0F, dtype=np.uint8)
        _write_nibbles(metadata, indices, tile_metadata)

    target_ids = mapping.ids[source_ids]
    blocks = target_ids.astype(np.uint8).tobytes()

    add = b""
    if mapping._high_targets and np.any(target_ids > 0xFF):
        target_high = (target_ids >> 8).astype(np.uint8)
        packed_high = target_high[::2] | (target_high[1::2] << 4)
        add = _array(ADD, packed_high.tobytes())

    data = metadata.tobytes()
    if mapping._metadata_overrides:
        target_metadata = mapping.metadata[source_ids]
        if np.any(target_metadata != PRESERVE_METADATA):
            low = np.where(
                target_metadata[::2] == PRESERVE_METADATA,
                metadata & 0x0F,
                target_metadata[::2],
            )
            high = np.where(
                target_metadata[1::2] == PRESERVE_METADATA,
                metadata >> 4,
                target_metadata[1::2],
            )
            data = (low | (high << 4)).astype(np.uint8).tobytes()

    return blocks, add, data


def _section(
    section: ChunkSection,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
    *,
    tile_indices: np.ndarray | None = None,
    tile_states: np.ndarray | None = None,
) -> bytes:
    blocks, add, data = _mapped_blocks(
        section,
        mapping,
        byte_mapping,
        tile_indices=tile_indices,
        tile_states=tile_states,
    )

    return b"".join(
        (
            Y,
            Y_VALUES[section.y],
            _array(BLOCKS, blocks),
            _array(DATA, data),
            _array(BLOCK_LIGHT, EMPTY_NIBBLES),
            add,
            _array(SKY_LIGHT, FULL_NIBBLES),
            bytes((Tag.END,)),
        )
    )


def _tile_materials_by_section(
    materials: ChunkTileMaterials | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    if materials is None:
        return None

    entries = np.frombuffer(materials, dtype=">u4")
    if not len(entries):
        return None

    positions = (entries >> 16).astype(np.uint16)
    section_y = positions >> 12
    indices = positions & 0x0FFF
    states = (entries & 0xFFFF).astype(np.uint16)
    return section_y, indices.astype(np.intp, copy=False), states


def chunk(
    cx: int,
    cz: int,
    source: RegionChunk,
    *,
    biomes: bool,
    materials: bool = True,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
) -> bytes:
    material_data = _tile_materials_by_section(source.materials) if materials else None
    sections = []
    for section in source.sections:
        tile_indices = None
        tile_states = None
        if material_data is not None:
            tile_y, all_indices, all_states = material_data
            selected = tile_y == section.y
            if np.any(selected):
                tile_indices = all_indices[selected]
                tile_states = all_states[selected]

        sections.append(
            _section(
                section,
                mapping,
                byte_mapping,
                tile_indices=tile_indices,
                tile_states=tile_states,
            )
        )

    biome_data = bytes(source.biomes)
    biome_data = _array(BIOMES, biome_data) * bool(biomes and any(biome_data))

    return b"".join(
        (
            ROOT,
            VERSION,
            LEVEL,
            XPOS,
            struct.pack(">i", cx),
            ZPOS,
            struct.pack(">i", cz),
            biome_data,
            SECTIONS,
            bytes((Tag.COMPOUND,)),
            struct.pack(">i", len(sections)),
            *sections,
            bytes((Tag.END, Tag.END)),
        )
    )
