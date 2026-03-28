from io import BytesIO
from uuid import UUID

import zstandard as zstd

from scfile.core.context.content import RegionContent
from scfile.core.decoder import FileDecoder
from scfile.core.io.streams import StructFileIO
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.region import ChunkHeader, RegionChunk


CHUNKS_COUNT = 32 * 32  # 1024

SECTION_SIZE = 16 * 16 * 16  # 4096
NIBBLE_SIZE = 16 * 16 * 8  # 2048


class MdatDecoder(FileDecoder[RegionContent], StructFileIO):
    format = FileFormat.NBT
    order = ByteOrder.BIG

    _content = RegionContent

    def parse(self):
        table = [(self._readb(F.I32), self._readb(F.I32), UUID(bytes=self.read(16))) for _ in range(CHUNKS_COUNT)]
        offsets, counts, uuids = map(list, zip(*table))

        dctx = zstd.ZstdDecompressor()
        chunks: list[RegionChunk] = []

        for index in range(CHUNKS_COUNT):
            if offsets[index] == 0:
                continue

            offset = offsets[index] * SECTION_SIZE
            self.seek(offset)

            # header
            full_size, blocks_mask, add_mask, fixed_size, compressed_size = self._readarray("I", 5).tolist()

            # read raw data
            compressed = self.read(compressed_size)
            decompressed = dctx.decompress(compressed)

            # split data
            sections_count = bin(blocks_mask).count("1")
            add_count = bin(add_mask).count("1")

            buffer = BytesIO(decompressed)
            blocks = buffer.read(sections_count * SECTION_SIZE)
            meta = buffer.read(sections_count * NIBBLE_SIZE)
            light = buffer.read(sections_count * NIBBLE_SIZE * 3)
            add = buffer.read(add_count * NIBBLE_SIZE)
            extra = buffer.read()

            chunks.append(
                RegionChunk(
                    index=index,
                    header=ChunkHeader(
                        full_size,
                        blocks_mask,
                        add_mask,
                        fixed_size,
                        compressed_size,
                    ),
                    blocks=blocks,
                    meta=meta,
                    light=light,
                    add=add,
                    extra=extra,
                )
            )

        self.data.offsets = offsets
        self.data.counts = counts
        self.data.uuid = uuids
        self.data.chunks = chunks
