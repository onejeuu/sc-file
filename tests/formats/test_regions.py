"""Public MDAT-to-MCA region conversion contracts."""

import struct
import zlib
from collections.abc import Sequence
from dataclasses import dataclass

import pytest
import zstandard

from scfile import Options, formats


_BLOCK_MAPPING = {
    "2401": "1",
    "2405": "1",
    "2414": "1",
    "2486": "1",
    "2488": "1",
    "2498": "1",
    "2499": "1!",
    "35": "35",
    "42": "42",
    "73": "42",
    "87": "4",
    "101": "101",
    "112": "112",
    "129": "42",
    "153": "101",
    "159": "159",
    "3113": "0",
    "3808": "83",
    "3826": "37",
    "4018": "0",
    "4025": "0",
}


@dataclass(frozen=True, slots=True)
class _Tile:
    position: tuple[int, int, int]
    source_id: int
    primary_cover: int
    faces: tuple[int, int, int, int, int, int] | None = None
    record_type: int = 0
    geometry: int = 0


def _tile_record(tile: _Tile) -> bytes:
    x, y, z = tile.position
    flags = 8 if tile.faces is not None else 0
    covers = (*tile.faces, tile.primary_cover) if tile.faces is not None else (tile.primary_cover,)
    data = struct.pack(">biiiB", tile.record_type, x, y, z, flags)
    data += struct.pack(f">{len(covers)}H", *covers)
    data += struct.pack(">I", tile.geometry & 0xFFFFFFFF)
    if tile.record_type == 1:
        data += struct.pack(">I", tile.geometry >> 32)
    return data


def _mdat_region(tiles: Sequence[_Tile]) -> bytes:
    """Build one minimal MDAT v5 chunk without touching the filesystem."""

    blocks = bytearray(16 * 16 * 16)
    additions = bytearray(2048)
    for tile in tiles:
        x, y, z = tile.position
        index = y * 256 + z * 16 + x
        blocks[index] = tile.source_id & 0xFF
        high = tile.source_id >> 8
        if index & 1:
            additions[index >> 1] |= high << 4
        else:
            additions[index >> 1] |= high

    # One block plane, metadata, three lighting planes, additions, biomes, records.
    terrain = bytes(blocks) + bytes(2048 * 4) + bytes(additions) + bytes(256)
    records = struct.pack(">i", len(tiles)) + b"".join(_tile_record(tile) for tile in tiles)
    payload = terrain + records
    compressed = zstandard.ZstdCompressor(level=1).compress(payload)

    # MDAT v5 has a 1024-entry table of 24-byte entries: six sectors.
    table = bytearray(6 * 4096)
    struct.pack_into(">ii16s", table, 0, 6, 0, bytes(16))
    header = struct.pack(">5i", len(payload), 1, 1, 0, len(compressed))
    return bytes(table) + header + compressed


def _convert(
    tiles: Sequence[_Tile],
    *,
    mdat_objects: bool = False,
    mdat_materials: bool = True,
) -> dict:
    source = _mdat_region(tiles)
    options = Options(
        mdat_version=5,
        mdat_objects=mdat_objects,
        mdat_materials=mdat_materials,
        mca_mappings=_BLOCK_MAPPING,
    )

    with formats.MdatDecoder(source, options=options) as decoder:
        mca = decoder.convert(formats.McaEncoder)

    location = int.from_bytes(mca[:4], "big")
    sector = location >> 8
    assert sector >= 2
    offset = sector * 4096
    length = struct.unpack_from(">I", mca, offset)[0]
    assert mca[offset + 4] == 2
    nbt_bytes = zlib.decompress(mca[offset + 5 : offset + 4 + length])

    with formats.NbtDecoder(nbt_bytes) as decoder:
        document = decoder.decode().value

    assert isinstance(document, dict)
    level = document["Level"]
    assert isinstance(level, dict)
    sections = level["Sections"]
    assert isinstance(sections, list) and len(sections) == 1
    section = sections[0]
    assert isinstance(section, dict)
    return section


def _state(section: dict, position: tuple[int, int, int]) -> tuple[int, int]:
    x, y, z = position
    index = y * 256 + z * 16 + x
    blocks = section["Blocks"]
    metadata = section["Data"]
    block_id = blocks[index]
    packed = metadata[index >> 1]
    block_metadata = (packed >> (4 if index & 1 else 0)) & 0x0F
    return block_id, block_metadata


def _cover(block_id: int, metadata: int = 0) -> int:
    return (metadata << 12) | block_id


def test_mdat_to_mca_uses_exposed_grid_area_to_resolve_face_tie() -> None:
    position = (1, 0, 1)
    section = _convert(
        (
            _Tile(
                position,
                2498,
                _cover(4018),
                faces=(0, _cover(159, 5), 0, _cover(153), 0, 0),
                record_type=1,
                geometry=0x0011002200440088,
            ),
        )
    )

    assert _state(section, position) == (159, 5)


@pytest.mark.parametrize(
    ("geometry", "faces", "expected"),
    (
        (1, (_cover(35), 0, 0, 0, _cover(159), 0), (159, 0)),
        (3, (_cover(35), 0, _cover(159), 0, 0, 0), (35, 0)),
        (5, (_cover(35), 0, _cover(159), 0, 0, 0), (159, 0)),
    ),
)
def test_mdat_to_mca_uses_box_face_area_for_each_half_block_axis(
    geometry: int,
    faces: tuple[int, int, int, int, int, int],
    expected: tuple[int, int],
) -> None:
    position = (geometry, 0, 2)
    section = _convert(
        (
            _Tile(
                position,
                2405,
                _cover(4018),
                faces=faces,
                geometry=geometry,
            ),
        )
    )

    assert _state(section, position) == expected


def test_mdat_to_mca_prefers_visible_primary_cover_over_side_covers() -> None:
    position = (4, 0, 2)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(42),
                faces=(0, _cover(159), 0, _cover(101), 0, 0),
            ),
        )
    )

    assert _state(section, position) == (42, 0)


def test_mdat_to_mca_uses_unique_face_majority_and_preserves_metadata() -> None:
    position = (4, 0, 3)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(4018),
                faces=(0, _cover(101), _cover(35, 11), _cover(35, 11), 0, 0),
            ),
        )
    )

    assert _state(section, position) == (35, 11)


def test_mdat_to_mca_leaves_equal_area_face_tie_as_air() -> None:
    position = (5, 0, 4)
    section = _convert(
        (
            _Tile(
                position,
                2405,
                _cover(4018),
                faces=(_cover(35), 0, _cover(159), 0, 0, 0),
                geometry=0,
            ),
        )
    )

    assert _state(section, position) == (0, 0)


def test_mdat_to_mca_leaves_unknown_box_geometry_tie_as_air() -> None:
    position = (6, 0, 4)
    section = _convert(
        (
            _Tile(
                position,
                2405,
                _cover(4018),
                faces=(_cover(35), 0, _cover(159), 0, 0, 0),
                geometry=7,
            ),
        )
    )

    assert _state(section, position) == (0, 0)


@pytest.mark.parametrize("source_id", (2486, 2401, 2405))
def test_mdat_to_mca_keeps_north_mines_invisible_walls_as_air(source_id: int) -> None:
    position = (3, 0, 5)
    section = _convert((_Tile(position, source_id, _cover(4018)),))

    assert _state(section, position) == (0, 0)


@pytest.mark.parametrize(
    ("source_id", "primary_cover", "faces", "record_type", "geometry", "expected"),
    (
        (2486, _cover(4018), (0, _cover(101), _cover(129), _cover(129), 0, 0), 0, 0, (42, 0)),
        (2414, _cover(4018), (0, 0, _cover(35, 11), 0, _cover(35, 11), 0), 0, 0, (35, 11)),
        (2498, _cover(4018), (_cover(35, 12), _cover(35, 12), 0, 0, 0, 0), 1, 1, (35, 12)),
        (2486, _cover(4025), (0, 0, 0, 0, _cover(87), 0), 0, 3, (4, 0)),
        (
            2498,
            _cover(4018),
            (0, _cover(159, 5), 0, _cover(153), 0, 0),
            1,
            0x0011002200440088,
            (159, 5),
        ),
        (2488, _cover(4018), (0, _cover(73), 0, 0, 0, 0), 0, 0, (42, 0)),
        (2414, _cover(4018), (0, 0, _cover(35, 11), 0, _cover(35, 11), 0), 0, 10, (35, 11)),
        (2405, _cover(3113), (0, 0, 0, 0, _cover(112), 0), 0, 2, (112, 0)),
    ),
)
def test_mdat_to_mca_restores_known_north_mines_blocks(
    source_id: int,
    primary_cover: int,
    faces: tuple[int, int, int, int, int, int],
    record_type: int,
    geometry: int,
    expected: tuple[int, int],
) -> None:
    position = (2, 0, 2)
    section = _convert(
        (
            _Tile(
                position,
                source_id,
                primary_cover,
                faces=faces,
                record_type=record_type,
                geometry=geometry,
            ),
        )
    )

    assert _state(section, position) == expected


def test_mdat_to_mca_allows_collapsible_upper_cover_when_target_is_full_cube() -> None:
    position = (3, 0, 3)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(4018),
                faces=(0, _cover(42), 0, 0, 0, 0),
                geometry=0x0035B083,
            ),
        )
    )

    assert _state(section, position) == (42, 0)


@pytest.mark.parametrize(
    ("cover", "geometry", "expected"),
    ((3808, 0x0035B083, 83), (3826, 0x00294D6B, 37)),
)
@pytest.mark.parametrize("mdat_objects", (False, True))
def test_mdat_to_mca_maps_collapsible_upper_cover_without_target_id_exceptions(
    cover: int,
    geometry: int,
    expected: int,
    mdat_objects: bool,
) -> None:
    position = (3, 0, 3)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(4018),
                faces=(0, _cover(cover), 0, 0, 0, 0),
                geometry=geometry,
            ),
        ),
        mdat_objects=mdat_objects,
    )

    assert _state(section, position) == (expected, 0)


def test_mdat_to_mca_uses_other_faces_when_collapsible_upper_cover_is_a_plant() -> None:
    position = (11, 0, 8)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(4018),
                faces=(_cover(35), _cover(3826), _cover(35), 0, 0, 0),
                geometry=0x0035B083,
            ),
        )
    )

    assert _state(section, position) == (35, 0)


def test_mdat_to_mca_does_not_filter_plant_cover_for_probuilder() -> None:
    position = (12, 0, 8)
    section = _convert(
        (
            _Tile(
                position,
                2498,
                _cover(4018),
                faces=(0, _cover(3826), 0, 0, 0, 0),
                record_type=1,
                geometry=0x0011002200440088,
            ),
        )
    )

    assert _state(section, position) == (37, 0)

def test_mdat_to_mca_respects_lock_except_for_explicit_air_primary() -> None:
    visible_position = (7, 0, 6)
    air_position = (8, 0, 6)
    section = _convert(
        (
            _Tile(
                visible_position,
                2499,
                _cover(42),
                faces=(0, _cover(159), 0, _cover(101), 0, 0),
            ),
            _Tile(
                air_position,
                2499,
                _cover(4018),
                faces=(0, _cover(159), 0, _cover(101), 0, 0),
            ),
        )
    )

    assert _state(section, visible_position) == (1, 0)
    assert _state(section, air_position) == (0, 0)


def test_mdat_to_mca_can_disable_material_record_application() -> None:
    position = (9, 0, 7)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(4018),
                faces=(0, _cover(42), _cover(35), _cover(35), 0, 0),
            ),
        ),
        mdat_materials=False,
    )

    assert _state(section, position) == (1, 0)


@pytest.mark.parametrize("mdat_objects", (False, True))
def test_mdat_to_mca_applies_same_tile_result_with_both_record_decode_modes(
    mdat_objects: bool,
) -> None:
    position = (10, 0, 8)
    section = _convert(
        (
            _Tile(
                position,
                2486,
                _cover(4018),
                faces=(0, _cover(42), _cover(35), _cover(35), 0, 0),
            ),
        ),
        mdat_objects=mdat_objects,
    )

    assert _state(section, position) == (35, 0)
