from uuid import UUID

import zstandard as zstd

from scfile.core.context.content import RegionContent
from scfile.core.decoder import FileDecoder
from scfile.core.io.streams import StructFileIO
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.region import RegionChunk


CHUNKS_COUNT = 32 * 32  # 1024
SECTION_SIZE = 16 * 16 * 16  # 4096


class MdatDecoder(FileDecoder[RegionContent], StructFileIO):
    format = FileFormat.NBT
    order = ByteOrder.BIG

    _content = RegionContent

    def parse(self):
        table = [(self._readb(F.I32), self._readb(F.I32), UUID(bytes=self.read(16))) for _ in range(CHUNKS_COUNT)]
        x1, x2, uuids = map(list, zip(*table))

        dctx = zstd.ZstdDecompressor()
        chunks: list[RegionChunk] = []

        for index in range(CHUNKS_COUNT):
            if x1[index] == 0:
                continue

            offset = x1[index] * 0x1000
            self.seek(offset)

            # header
            h1, h2, h3, h4, compressed_size = self._readarray("I", 5).tolist()

            # read raw data
            compressed = self.read(compressed_size)
            decompressed = dctx.decompress(compressed)

            # split data
            sections = bin(h2).count("1")
            buffer = sections * SECTION_SIZE
            terrain, remain = decompressed[:buffer], decompressed[buffer:]

            chunks.append(RegionChunk(index, terrain, remain))

        self.data.x1 = x1
        self.data.x2 = x2
        self.data.uuid = uuids
        self.data.chunks = chunks
