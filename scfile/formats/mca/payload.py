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


def _projected_planes(
    section: ChunkSection,
    indices: np.ndarray | None,
    states: np.ndarray | None,
) -> tuple[bytes, memoryview | bytes | None, bytes]:
    if indices is None or states is None or not len(indices):
        return (
            bytes(section.blocks),
            section.additions,
            bytes(section.metadata),
        )

    blocks = np.frombuffer(section.blocks, dtype=np.uint8).copy()
    metadata = np.frombuffer(section.metadata, dtype=np.uint8).copy()
    additions = None if section.additions is None else np.frombuffer(section.additions, dtype=np.uint8).copy()

    block_ids = states & 0x0FFF
    metadata_values = ((states >> 12) & 0x0F).astype(np.uint8)
    blocks[indices] = (block_ids & 0xFF).astype(np.uint8)
    _write_nibbles(metadata, indices, metadata_values)

    if additions is not None or np.any(block_ids > 0xFF):
        if additions is None:
            additions = np.zeros(NIBBLE_SIZE, dtype=np.uint8)
        _write_nibbles(additions, indices, ((block_ids >> 8) & 0x0F).astype(np.uint8))

    return blocks.tobytes(), None if additions is None else additions.tobytes(), metadata.tobytes()


def _mapped_blocks(
    section: ChunkSection,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
    *,
    tile_indices: np.ndarray | None = None,
    tile_states: np.ndarray | None = None,
) -> tuple[bytes, bytes, bytes]:
    blocks, additions, metadata = _projected_planes(section, tile_indices, tile_states)

    if (
        additions is None
        and byte_mapping is not None
        and (mapping._low_metadata_mask is None or b"\x01" not in blocks.translate(mapping._low_metadata_mask))
    ):
        return blocks.translate(byte_mapping), b"", metadata

    source_ids = np.frombuffer(blocks, dtype=np.uint8).astype(np.uint16)

    if additions is not None:
        packed = np.frombuffer(additions, dtype=np.uint8)
        source_ids[::2] |= (packed & 0x0F).astype(np.uint16) << 8
        source_ids[1::2] |= (packed >> 4).astype(np.uint16) << 8

    target_ids = mapping.ids[source_ids]
    blocks = target_ids.astype(np.uint8).tobytes()

    target_high = (target_ids >> 8).astype(np.uint8)
    packed_high = target_high[::2] | (target_high[1::2] << 4)
    add = _array(ADD, packed_high.tobytes()) if np.any(packed_high) else b""

    data = metadata
    if mapping._has_metadata_overrides:
        target_meta = mapping.metadata[source_ids]
        if np.any(target_meta != PRESERVE_METADATA):
            packed_data = np.frombuffer(data, dtype=np.uint8)
            low = np.where(target_meta[::2] == PRESERVE_METADATA, packed_data & 0x0F, target_meta[::2])
            high = np.where(target_meta[1::2] == PRESERVE_METADATA, packed_data >> 4, target_meta[1::2])
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

    positions = np.frombuffer(materials.positions, dtype=">i4").reshape(-1, 3)
    states = np.frombuffer(materials.states, dtype=">u2")
    if not len(positions):
        return None

    x, y, z = positions.T
    selected = (y >= 0) & (y < 256)
    if not np.any(selected):
        return None

    x = (x[selected] & 15).astype(np.intp, copy=False)
    y = y[selected]
    z = (z[selected] & 15).astype(np.intp, copy=False)
    indices = ((y & 15) << 8) | (z << 4) | x
    return (y >> 4), indices.astype(np.intp, copy=False), states[selected]


def chunk(
    cx: int,
    cz: int,
    source: RegionChunk,
    *,
    export_biomes: bool,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
) -> bytes:
    materials = _tile_materials_by_section(source.materials)
    sections = []
    for section in source.sections:
        tile_indices = None
        tile_states = None
        if materials is not None:
            tile_y, all_indices, all_states = materials
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

    biomes = bytes(source.biomes)
    biomes = _array(BIOMES, biomes) * bool(export_biomes and any(biomes))

    return b"".join(
        (
            ROOT,
            VERSION,
            LEVEL,
            XPOS,
            struct.pack(">i", cx),
            ZPOS,
            struct.pack(">i", cz),
            biomes,
            SECTIONS,
            bytes((Tag.COMPOUND,)),
            struct.pack(">i", len(sections)),
            *sections,
            bytes((Tag.END, Tag.END)),
        )
    )
