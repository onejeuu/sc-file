from typing import override

import zstandard as zstd

from scfile.content import RegionContent
from scfile.content import regions as S
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.exceptions import BinaryStructureError

from . import payload


CHUNK_COUNT = 32 * 32
SECTOR_SIZE = 4096


class MdatDecoder(Decoder[RegionContent]):
    format = FileFormat.MDAT
    order = ByteOrder.BIG

    content_type = RegionContent

    @override
    def _parse(self):
        table = [
            (
                self.io.value(F.I32),
                self.io.value(F.I32),
                self.io.read(16),
            )
            for _ in range(CHUNK_COUNT)
        ]
        offsets, counts, uuids = map(list, zip(*table))

        zctx = zstd.ZstdDecompressor()
        chunks: list[S.RegionChunk] = []

        for index, sector in enumerate(offsets):
            if sector == 0:
                continue

            chunks.append(self._parse_chunk(index, sector, zctx))

        self.data.offsets = offsets
        self.data.counts = counts
        self.data.uuids = uuids
        self.data.chunks = chunks

    def _parse_chunk(
        self,
        index: int,
        sector: int,
        zctx: zstd.ZstdDecompressor,
    ) -> S.RegionChunk:
        self.io.seek(sector * SECTOR_SIZE)
        header = S.ChunkHeader(*self.io.array(F.U32, 5).tolist())

        position = self.io.tell()
        compressed = self.io.read_exact(header.compressed_size)

        try:
            data = zctx.decompress(compressed)

        except zstd.ZstdError as error:
            raise BinaryStructureError(
                location=self.location,
                offset=position,
            ) from error

        return payload.chunk(
            index,
            header,
            data,
            extended=self.options.extended_chunk,
        )
