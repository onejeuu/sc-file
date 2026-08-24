import struct

from scfile.content.regions import RegionChunk
from scfile.io.nbt import Tag

from .mapping import BLOCKS_MAPPING


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


def _section(
    y: int,
    blocks: bytes,
) -> bytes:
    return b"".join(
        (
            Y,
            Y_VALUES[y],
            _array(BLOCKS, blocks),
            _array(DATA, EMPTY_NIBBLES),
            _array(BLOCK_LIGHT, EMPTY_NIBBLES),
            _array(ADD, EMPTY_NIBBLES),
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
) -> bytes:
    sections = [_section(section.y, bytes(section.blocks).translate(BLOCKS_MAPPING)) for section in source.sections]
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
