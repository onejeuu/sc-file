import struct
import zlib
from typing import override

from scfile.content import RegionContent
from scfile.content.regions import RegionChunk
from scfile.core import Encoder
from scfile.enums import ByteOrder, FileFormat
from scfile.io.nbt import Tag

from .mapping import BLOCKS_MAPPING


VERSION = Tag.INT.header(b"DataVersion") + struct.pack(">i", 1343)  # Anvil 1.12.2

ZLIB_COMPRESSION = b"\x02"

CURRENT_TIME = 0
TIMESTAMPS = struct.pack(">I", CURRENT_TIME) * 1024

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


def byte_array(
    header: bytes,
    data: bytes,
) -> bytes:
    return header + struct.pack(">i", len(data)) + data


def section_payload(
    y: int,
    blocks: bytes,
) -> bytes:
    return b"".join(
        (
            Y,
            Y_VALUES[y],
            byte_array(BLOCKS, blocks),
            byte_array(DATA, EMPTY_NIBBLES),
            byte_array(BLOCK_LIGHT, EMPTY_NIBBLES),
            byte_array(ADD, EMPTY_NIBBLES),
            byte_array(SKY_LIGHT, FULL_NIBBLES),
            bytes((Tag.END,)),
        )
    )


class McaEncoder(Encoder[RegionContent]):
    format = FileFormat.MCA
    order = ByteOrder.BIG

    content_type = RegionContent

    @override
    def _serialize(self):
        # Create region header
        location_table = bytearray(4096)
        parts = [location_table, TIMESTAMPS]

        current_sector = 2
        marker_size = len(ZLIB_COMPRESSION)

        for chunk in self.data.chunks:
            # Resolve world coordinates
            local_x, local_z = chunk.index % 32, chunk.index // 32
            chunk_x, chunk_z = self.data.rx * 32 + local_x, self.data.rz * 32 + local_z

            # Encode chunk
            compressed = zlib.compress(self._chunk(chunk_x, chunk_z, chunk), level=3)
            record = struct.pack(">I", marker_size + len(compressed)) + ZLIB_COMPRESSION + compressed

            # Pad sector
            record_size = len(record)
            sector_count = (record_size + 4096 - 1) // 4096
            parts.append(record)

            padding = (sector_count * 4096) - record_size
            parts.append(b"\x00" * padding)

            # Update chunk location
            entry = (local_x + local_z * 32) * 4
            location = (current_sector << 8) | sector_count
            location_table[entry : entry + 4] = location.to_bytes(4, "big")

            current_sector += sector_count

        self.io.write(b"".join(parts))

    def _chunk(self, cx: int, cz: int, chunk: RegionChunk) -> bytes:
        sections: list[bytes] = []

        for source in chunk.sections:
            blocks = bytes(source.blocks).translate(BLOCKS_MAPPING)
            sections.append(section_payload(source.y, blocks))

        biomes = bytes(chunk.biomes)
        biomes_data = byte_array(BIOMES, biomes) * bool(self.options.biomes and any(biomes))
        return b"".join(
            (
                ROOT,
                VERSION,
                LEVEL,
                XPOS,
                struct.pack(">i", cx),
                ZPOS,
                struct.pack(">i", cz),
                biomes_data,
                SECTIONS,
                bytes((Tag.COMPOUND,)),
                struct.pack(">i", len(sections)),
                *sections,
                bytes((Tag.END, Tag.END)),
            )
        )
