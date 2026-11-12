import struct
from dataclasses import dataclass

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

BOX_BLOCK_ID = 2405
PROBUILDER_BLOCK_ID = 2498
FACE_BYTE_OFFSETS = np.arange(12, dtype=np.intp)
FACE_BYTE_OFFSETS.flags.writeable = False


BOX_SURFACE_AREAS = (
    (2, 2, 2, 2, 2, 2),
    (1, 1, 1, 1, 2, 2),
    (1, 1, 1, 1, 2, 2),
    (2, 2, 1, 1, 1, 1),
    (2, 2, 1, 1, 1, 1),
    (1, 1, 2, 2, 1, 1),
    (1, 1, 2, 2, 1, 1),
)


@dataclass(frozen=True, slots=True)
class _TileStates:
    indices: np.ndarray
    states: np.ndarray


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
    lut = mapping._low_lut
    if mask is None or lut is None or b"\x01" not in source_blocks.translate(mask):
        return metadata.tobytes()

    source_ids = np.frombuffer(source_blocks, dtype=np.uint8)
    low = lut[source_ids[::2], metadata & 0x0F]
    high = lut[source_ids[1::2], metadata >> 4]
    return (low | (high << 4)).tobytes()


def _tile_source_ids(section: ChunkSection, indices: np.ndarray) -> np.ndarray:
    source_ids = np.frombuffer(section.blocks, dtype=np.uint8)[indices].astype(np.uint16)

    if section.additions is not None:
        additions = np.frombuffer(section.additions, dtype=np.uint8)[indices >> 1]
        high = np.where((indices & 1) == 0, additions & 0x0F, additions >> 4)
        source_ids |= high.astype(np.uint16) << 8

    return source_ids


def _grid_surface_areas(mask: int) -> tuple[int, int, int, int, int, int]:
    layers = tuple((mask >> (16 * y)) & 0xFFFF for y in range(4))
    down = layers[0].bit_count()
    up = layers[3].bit_count()

    for y in range(1, 4):
        down += (layers[y] & ~layers[y - 1]).bit_count()

    for y in range(3):
        up += (layers[y] & ~layers[y + 1]).bit_count()

    north = south = west = east = 0
    for layer in layers:
        rows = tuple((layer >> (4 * z)) & 0x0F for z in range(4))
        for z, row in enumerate(rows):
            north += (row if z == 0 else row & ~rows[z - 1]).bit_count()
            south += (row if z == 3 else row & ~rows[z + 1]).bit_count()
            west += (row & ~(row << 1)).bit_count()
            east += (row & ~(row >> 1)).bit_count()

    return down, up, north, south, west, east


def _surface_areas(source_id: int, record_type: int, geometry: int) -> tuple[int, ...] | None:
    if source_id == PROBUILDER_BLOCK_ID and record_type == 1:
        return _grid_surface_areas(geometry)
    if source_id == BOX_BLOCK_ID and record_type == 0 and 0 <= geometry < len(BOX_SURFACE_AREAS):
        return BOX_SURFACE_AREAS[geometry]
    return None


def _weighted_face_state(
    states: np.ndarray,
    visible: np.ndarray,
    areas: tuple[int, ...],
) -> int | None:
    totals: dict[int, int] = {}
    for side, area in enumerate(areas):
        if area and visible[side]:
            state = int(states[side])
            totals[state] = totals.get(state, 0) + area

    if not totals:
        return None

    maximum = max(totals.values())
    winners = [state for state, area in totals.items() if area == maximum]
    return winners[0] if len(winners) == 1 else None


def _fallback_tile_states(
    mapped_states: np.ndarray,
    source_ids: np.ndarray,
    candidates: np.ndarray,
    mapping: CompiledBlockMapping,
    materials: ChunkTileMaterials,
) -> None:
    face_map = np.frombuffer(materials.face_map, dtype=np.uint64)
    if not len(face_map):
        return

    face_entries = (face_map >> 32).astype(np.intp)
    face_rows = np.flatnonzero(candidates[face_entries])
    if not len(face_rows):
        return

    candidate_rows = face_entries[face_rows]
    offsets = (face_map[face_rows] & 0xFFFFFFFF).astype(np.intp)
    raw = np.frombuffer(materials.record_data, dtype=np.uint8)
    packed = raw[offsets[:, None] + FACE_BYTE_OFFSETS]
    source_faces = (packed[:, 0::2].astype(np.uint16) << 8) | packed[:, 1::2].astype(np.uint16)
    states = mapping._state_lut[source_faces]
    visible = (states & 0x0FFF) != 0
    has_visible = np.any(visible, axis=1)
    if not np.any(has_visible):
        return

    candidate_rows = candidate_rows[has_visible]
    face_rows = face_rows[has_visible]
    states = states[has_visible]
    visible = visible[has_visible]

    frequencies = np.zeros(states.shape, dtype=np.uint8)
    for side in range(6):
        frequencies[:, side] = np.count_nonzero(
            (states == states[:, side, None]) & visible,
            axis=1,
        )

    winners = (frequencies == frequencies.max(axis=1, keepdims=True)) & visible
    winner_indices = winners.argmax(axis=1)
    winning_states = states[np.arange(len(states)), winner_indices]
    unique_mode = np.all(~winners | (states == winning_states[:, None]), axis=1)

    mapped_states[candidate_rows[unique_mode]] = winning_states[unique_mode]

    shape_data = np.frombuffer(materials.shape_data, dtype=">u8")
    record_types = np.frombuffer(materials.record_types, dtype=np.uint8)
    for index in np.flatnonzero(~unique_mode):
        row = candidate_rows[index]
        face_row = face_rows[index]
        areas = _surface_areas(int(source_ids[row]), int(record_types[face_row]), int(shape_data[face_row]))
        if areas is None:
            continue
        state = _weighted_face_state(states[index], visible[index], areas)
        if state is not None:
            mapped_states[row] = state


def _mapped_blocks(
    section: ChunkSection,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
    tiles: _TileStates | None = None,
) -> tuple[bytes, bytes, bytes]:
    if section.additions is None and byte_mapping is not None:
        source_blocks = bytes(section.blocks)
        if tiles is None:
            blocks = source_blocks.translate(byte_mapping)
            metadata = np.frombuffer(section.metadata, dtype=np.uint8)
            data = _mapped_low_metadata(source_blocks, metadata, mapping)
            return blocks, b"", data

        indices, states = tiles.indices, tiles.states
        tile_ids = states & 0x0FFF
        if not np.any(tile_ids > 0xFF):
            blocks = np.frombuffer(
                bytearray(source_blocks.translate(byte_mapping)),
                dtype=np.uint8,
            )
            blocks[indices] = tile_ids.astype(np.uint8)

            metadata = np.frombuffer(section.metadata, dtype=np.uint8)
            data = bytearray(_mapped_low_metadata(source_blocks, metadata, mapping))
            mapped_metadata = np.frombuffer(data, dtype=np.uint8)
            tile_metadata = (states >> 12).astype(np.uint8)
            _write_nibbles(mapped_metadata, indices, tile_metadata)
            return blocks.tobytes(), b"", bytes(data)

    source_ids = np.frombuffer(section.blocks, dtype=np.uint8).astype(np.uint16)
    if section.additions is not None:
        packed = np.frombuffer(section.additions, dtype=np.uint8)
        source_ids[::2] |= (packed & 0x0F).astype(np.uint16) << 8
        source_ids[1::2] |= (packed >> 4).astype(np.uint16) << 8

    metadata = np.frombuffer(section.metadata, dtype=np.uint8)
    target_ids = mapping.ids[source_ids]

    target_metadata = metadata.copy()
    if mapping._metadata_overrides:
        overrides = mapping.metadata[source_ids]
        indices = np.flatnonzero(overrides != PRESERVE_METADATA)
        _write_nibbles(target_metadata, indices, overrides[indices])

    if tiles is not None:
        target_ids[tiles.indices] = tiles.states & 0x0FFF
        _write_nibbles(target_metadata, tiles.indices, (tiles.states >> 12).astype(np.uint8))

    blocks = target_ids.astype(np.uint8).tobytes()
    add = b""
    if mapping._high_targets and np.any(target_ids > 0xFF):
        target_high = (target_ids >> 8).astype(np.uint8)
        packed_high = target_high[::2] | (target_high[1::2] << 4)
        add = _array(ADD, packed_high.tobytes())

    return blocks, add, target_metadata.tobytes()


def _section(
    section: ChunkSection,
    mapping: CompiledBlockMapping,
    byte_mapping: bytes | None,
    tiles: _TileStates | None = None,
) -> bytes:
    blocks, add, data = _mapped_blocks(section, mapping, byte_mapping, tiles)

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
    source: RegionChunk,
    mapping: CompiledBlockMapping,
) -> dict[int, _TileStates]:
    materials = source.materials
    if materials is None:
        return {}

    entries = np.frombuffer(materials.entries, dtype=">u4")
    if not len(entries):
        return {}

    section_y = (entries >> 28).astype(np.uint8)
    indices = ((entries >> 16) & 0x0FFF).astype(np.uint16)
    source_ids = np.zeros(len(entries), dtype=np.uint16)
    section_rows = {}
    for section in source.sections:
        rows = np.flatnonzero(section_y == section.y)
        if len(rows):
            section_rows[section.y] = rows
            source_ids[rows] = _tile_source_ids(section, indices[rows])

    states = mapping._state_lut[entries & 0xFFFF]
    source_non_air = mapping.ids[source_ids] != 0
    locked = mapping._tile_locked[source_ids]
    candidates = ((states & 0x0FFF) == 0) & source_non_air & ~locked
    if np.any(candidates):
        _fallback_tile_states(states, source_ids, candidates, mapping, materials)

    apply = source_non_air & (~locked | ((states & 0x0FFF) == 0))
    result = {}
    for y, rows in section_rows.items():
        rows = rows[apply[rows]]
        if len(rows):
            result[y] = _TileStates(indices[rows], states[rows])
    return result


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
    tiles = _tile_materials_by_section(source, mapping) if materials else {}
    sections = [_section(section, mapping, byte_mapping, tiles.get(section.y)) for section in source.sections]

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
