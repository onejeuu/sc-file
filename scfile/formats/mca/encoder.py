import struct
import time
import zlib

from scfile.core.context.content import RegionContent
from scfile.core.encoder import FileEncoder
from scfile.core.io.streams import StructBytesIO
from scfile.enums import ByteOrder, FileFormat
from scfile.formats.nbt.enums import Tag
from scfile.structures.regions import RegionChunk

from . import nbt
from .mapping import BLOCKS_MAPPING


_VERSION = nbt.encode_int(b"DataVersion", 1343)  # Anvil 1.12.2

_CURRENT_TIME = int(time.time())
_TIMESTAMPS = struct.pack(">I", _CURRENT_TIME) * 1024

_ROOT_COMPOUND = nbt.encode(Tag.COMPOUND, b"")
_LEVEL_HEAD = nbt.encode(Tag.COMPOUND, b"Level")
_XPOS_HEAD = nbt.encode(Tag.INT, b"xPos")
_ZPOS_HEAD = nbt.encode(Tag.INT, b"zPos")
_SECTIONS_HEAD = nbt.encode(Tag.LIST, b"Sections")
_Y_HEAD = nbt.encode(Tag.BYTE, b"Y")
_BLOCKS_HEAD = nbt.encode(Tag.BYTE_ARRAY, b"Blocks")

_SECTION_SIZE = struct.pack(">i", 4096)
_Y_PACKED = [struct.pack(">b", y) for y in range(16)]

_PAYLOAD_CHUNK = (
    nbt.encode_ba(b"Data", bytes(2048))
    + nbt.encode_ba(b"BlockLight", bytes(2048))
    + nbt.encode_ba(b"Add", bytes(2048))
    + nbt.encode_ba(b"SkyLight", b"\xff" * 2048)
    + b"\x00"
)


class McaEncoder(FileEncoder[RegionContent], StructBytesIO):
    format = FileFormat.MCA
    order = ByteOrder.BIG

    def serialize(self):
        locations = bytearray(4096)
        timestamps = _TIMESTAMPS

        payload = [locations, timestamps]
        current_sector = len(payload)

        for chunk in self.data.chunks:
            lx, lz = chunk.index % 32, chunk.index // 32
            cx, cz = self.data.rx * 32 + lx, self.data.rz * 32 + lz

            compression_type = b"\x02"
            compressed_data = zlib.compress(self._chunk(cx, cz, chunk), level=3)

            data = struct.pack(">I", len(compressed_data) + len(compression_type)) + compression_type + compressed_data

            total_bytes = len(data)
            sectors_needed = (total_bytes + 4096 - 1) // 4096

            payload.append(data)

            padding = (sectors_needed * 4096) - total_bytes
            payload.append(b"\x00" * padding)

            idx = (lx + lz * 32) * 4
            locations[idx : idx + 4] = ((current_sector << 8) | sectors_needed).to_bytes(4, "big")

            current_sector += sectors_needed

        self.write(b"".join(payload))

    def _chunk(self, cx: int, cz: int, chunk: RegionChunk) -> bytes:
        blocks = chunk.blocks if self.options.parse_region_raw else chunk.blocks.translate(BLOCKS_MAPPING)
        mask = chunk.header.blocks_mask

        sections: list[bytes] = []

        present = [y for y in range(16) if (mask >> y) & 1]
        for idx, y in enumerate(present):
            section = blocks[idx * 4096 : (idx + 1) * 4096]
            sections.append(b"".join([_Y_HEAD, _Y_PACKED[y], _BLOCKS_HEAD, _SECTION_SIZE, section, _PAYLOAD_CHUNK]))

        return b"".join(
            [
                _ROOT_COMPOUND,
                _VERSION,
                _LEVEL_HEAD,
                _XPOS_HEAD,
                struct.pack(">i", cx),
                _ZPOS_HEAD,
                struct.pack(">i", cz),
                _SECTIONS_HEAD,
                b"\x0a",
                struct.pack(">i", len(sections)),
                b"".join(sections),
                b"\x00\x00",
            ]
        )
