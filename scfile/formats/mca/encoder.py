import struct
import zlib
from typing import override

from scfile.content import RegionContent
from scfile.core import Encoder
from scfile.enums import ByteOrder, FileFormat

from . import payload


TIMESTAMPS: bytes = struct.pack(">I", 0) * 1024
COMPRESSION_LEVEL: int = 3


class McaEncoder(Encoder[RegionContent]):
    format = FileFormat.MCA
    order = ByteOrder.BIG

    content_type = RegionContent

    @override
    def _serialize(self):
        # Create region header
        location_table = bytearray(4096)
        parts = [location_table, TIMESTAMPS]

        marker = b"\x02"
        marker_size = len(marker)

        current_sector = 2

        for chunk in self.data.chunks:
            # Resolve world coordinates
            local_x, local_z = chunk.index % 32, chunk.index // 32
            chunk_x, chunk_z = self.data.x * 32 + local_x, self.data.z * 32 + local_z

            # Encode chunk
            compressed = zlib.compress(
                payload.chunk(chunk_x, chunk_z, chunk, export_biomes=self.options.biomes),
                level=COMPRESSION_LEVEL,
            )
            record = struct.pack(">I", marker_size + len(compressed)) + marker + compressed

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
