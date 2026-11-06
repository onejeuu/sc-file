import struct

import numpy as np
from numpy.typing import NDArray

from scfile.content.regions import ChunkSection, RegionChunk
from scfile.io.nbt import Tag


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


def _mapped_blocks(
    section: ChunkSection,
    mapping: NDArray[np.uint16],
    byte_mapping: bytes | None,
) -> tuple[bytes, bytes]:
    additions = section.additions

    if additions is None and byte_mapping is not None:
        return bytes(section.blocks).translate(byte_mapping), b""

    source_ids = np.frombuffer(section.blocks, dtype=np.uint8).astype(np.uint16)

    if additions is not None:
        packed = np.frombuffer(additions, dtype=np.uint8)
        source_ids[::2] |= (packed & 0x0F).astype(np.uint16) << 8
        source_ids[1::2] |= (packed >> 4).astype(np.uint16) << 8

    target_ids = mapping[source_ids]
    blocks = target_ids.astype(np.uint8).tobytes()

    target_high = (target_ids >> 8).astype(np.uint8)
    packed_high = target_high[::2] | (target_high[1::2] << 4)
    add = _array(ADD, packed_high.tobytes()) if np.any(packed_high) else b""

    return blocks, add


def _section(
    section: ChunkSection,
    mapping: NDArray[np.uint16],
    byte_mapping: bytes | None,
) -> bytes:
    blocks, add = _mapped_blocks(section, mapping, byte_mapping)

    return b"".join(
        (
            Y,
            Y_VALUES[section.y],
            _array(BLOCKS, blocks),
            _array(DATA, bytes(section.metadata)),
            _array(BLOCK_LIGHT, EMPTY_NIBBLES),
            add,
            _array(SKY_LIGHT, FULL_NIBBLES),
            bytes((Tag.END,)),
        )
    )


def chunk(
    cx: int,
    cz: int,
    source: RegionChunk,
    *,
    export_biomes: bool,
    mapping: NDArray[np.uint16],
    byte_mapping: bytes | None,
) -> bytes:
    sections = [_section(section, mapping, byte_mapping) for section in source.sections]
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
