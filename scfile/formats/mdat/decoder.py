from uuid import UUID

import numpy as np
import zstandard as zstd

from scfile.core.context.content import RegionContent
from scfile.core.decoder import FileDecoder
from scfile.core.io.streams import StructFileIO
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.region import RegionChunk


SIZE = 32 * 32


class MdatDecoder(FileDecoder[RegionContent], StructFileIO):
    format = FileFormat.NBT
    order = ByteOrder.BIG

    _content = RegionContent

    def parse(self):
        table = [(self._readb(F.I32), self._readb(F.I32), UUID(bytes=self.read(16))) for _ in range(SIZE)]
        x1, x2, uuids = map(np.array, zip(*table))

        dctx = zstd.ZstdDecompressor()
        chunks: list[RegionChunk] = []

        for index in range(SIZE):
            if x1[index] == 0:
                continue

            offset = x1[index] * 0x1000
            self.seek(offset)

            # header
            size, h1, h2, uncsize, csize = self._readarray("I", 5).tolist()

            # data
            compressed = self.read(csize)
            decompressed = dctx.decompress(compressed)

            chunks.append(RegionChunk(index, decompressed))

            # padding
            # self.seek((self.tell() + 0xFFF) & ~0xFFF)

        self.data.x1 = x1.tolist()
        self.data.x2 = x2.tolist()
        self.data.uuid = uuids.tolist()
        self.data.chunks = chunks
