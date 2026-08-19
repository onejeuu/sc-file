from typing import override

import zstandard as zstd

from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.exceptions import BinaryStructureError
from scfile.structures import regions as S
from scfile.structures.content import RegionContent


CHUNK_COUNT = 32 * 32
SECTOR_SIZE = 4096
SECTION_SIZE = 16 * 16 * 16
NIBBLE_SIZE = SECTION_SIZE // 2
BIOME_SIZE = 16 * 16


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
        sector_offsets, sector_counts, uuids = map(list, zip(*table))

        zctx = zstd.ZstdDecompressor()
        chunks: list[S.RegionChunk] = []

        for index, sector in enumerate(sector_offsets):
            if sector == 0:
                continue

            chunks.append(self._parse_chunk(index, sector, zctx))

        self.data.sector_offsets = sector_offsets
        self.data.sector_counts = sector_counts
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
            payload = zctx.decompress(compressed)

        except zstd.ZstdError as error:
            raise BinaryStructureError(
                location=self.location,
                offset=position,
            ) from error

        section_count = header.section_mask.bit_count()
        cursor = section_count * SECTION_SIZE
        chunk = S.RegionChunk(
            index=index,
            header=header,
            blocks=payload[:cursor],
        )

        if not self.options.full_chunk:
            return chunk

        # Section layout:
        # blocks | metadata | block/sky light | add blocks | biomes | trailing data
        metadata_size = section_count * NIBBLE_SIZE
        add_size = header.add_mask.bit_count() * NIBBLE_SIZE
        chunk.meta = payload[cursor : (cursor := cursor + metadata_size)]
        chunk.light = payload[cursor : (cursor := cursor + metadata_size * 3)]
        chunk.add = payload[cursor : (cursor := cursor + add_size)]
        chunk.biomes = payload[cursor : (cursor := cursor + BIOME_SIZE)]
        chunk.extra = payload[cursor:]
        return chunk
