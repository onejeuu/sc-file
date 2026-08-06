import struct
import zlib
from typing import override

from scfile.core import Encoder, RegionContent
from scfile.enums import ByteOrder, FileFormat
from scfile.formats.nbt import nbt
from scfile.formats.nbt.enums import Tag
from scfile.structures.regions import RegionChunk

from .mapping import BLOCKS_MAPPING


VERSION = nbt.encode_int(b"DataVersion", 1343)  # Anvil 1.12.2

ZLIB_COMPRESSION = b"\x02"

CURRENT_TIME = 0
TIMESTAMPS = struct.pack(">I", CURRENT_TIME) * 1024

ROOT = nbt.encode(Tag.COMPOUND, b"")
LEVEL = nbt.encode(Tag.COMPOUND, b"Level")
XPOS = nbt.encode(Tag.INT, b"xPos")
ZPOS = nbt.encode(Tag.INT, b"zPos")
SECTIONS = nbt.encode(Tag.LIST, b"Sections")
Y = nbt.encode(Tag.BYTE, b"Y")
BLOCKS = nbt.encode(Tag.BYTE_ARRAY, b"Blocks")

SECTION_LENGTH = struct.pack(">i", 4096)
Y_VALUES = [struct.pack(">b", y) for y in range(16)]

SECTION_PAYLOAD = (
    nbt.encode_ba(b"Data", bytes(2048))
    + nbt.encode_ba(b"BlockLight", bytes(2048))
    + nbt.encode_ba(b"Add", bytes(2048))
    + nbt.encode_ba(b"SkyLight", b"\xff" * 2048)
    + b"\x00"
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
        blocks = chunk.blocks if self.options.raw_blocks else chunk.blocks.translate(BLOCKS_MAPPING)
        mask = chunk.header.section_mask

        sections: list[bytes] = []

        # Select present sections
        present = [y for y in range(16) if (mask >> y) & 1]
        for idx, y in enumerate(present):
            section = blocks[idx * 4096 : (idx + 1) * 4096]
            sections.append(b"".join([Y, Y_VALUES[y], BLOCKS, SECTION_LENGTH, section, SECTION_PAYLOAD]))

        # Build region NBT
        return b"".join(
            [
                ROOT,
                VERSION,
                LEVEL,
                XPOS,
                struct.pack(">i", cx),
                ZPOS,
                struct.pack(">i", cz),
                SECTIONS,
                b"\x0a",
                struct.pack(">i", len(sections)),
                b"".join(sections),
                b"\x00\x00",
            ]
        )
