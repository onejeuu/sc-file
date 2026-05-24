import zstandard as zstd

from scfile import formats
from scfile.core import FileDecoder, RegionContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import regions as S


CHUNKS_COUNT = 32 * 32  # 1024
SECTION_SIZE = 16 * 16 * 16  # 4096
NIBBLE_SIZE = 16 * 16 * 8  # 2048


class MdatDecoder(FileDecoder[RegionContent]):
    format = FileFormat.MDAT
    order = ByteOrder.BIG

    _content = RegionContent

    def as_mca(self):
        return self.convert_to(formats.mca.McaEncoder)

    def parse(self):
        table = [(self._readb(F.I32), self._readb(F.I32), self.read(16)) for _ in range(CHUNKS_COUNT)]
        offsets, counts, uuids = map(list, zip(*table))

        dctx = zstd.ZstdDecompressor()
        chunks: list[S.RegionChunk] = []

        for index in range(CHUNKS_COUNT):
            offset = offsets[index]
            if offset == 0:
                continue

            self.seek(offset * SECTION_SIZE)

            # header
            full_size, blocks_mask, add_mask, fixed_size, compressed_size = self._readarray(F.U32, 5).tolist()

            # read raw data
            compressed = self.read(compressed_size)
            decompressed = dctx.decompress(compressed)

            # split data
            pos = 0
            sections_count = bin(blocks_mask).count("1")
            blocks = decompressed[pos : (pos := pos + sections_count * SECTION_SIZE)]

            chunk = S.RegionChunk(
                index=index,
                header=S.ChunkHeader(full_size, blocks_mask, add_mask, fixed_size, compressed_size),
                blocks=blocks,
            )

            if self.options.full_chunk:
                add_count = bin(add_mask).count("1")
                chunk.meta = decompressed[pos : (pos := pos + sections_count * NIBBLE_SIZE)]
                chunk.light = decompressed[pos : (pos := pos + sections_count * NIBBLE_SIZE * 3)]
                chunk.add = decompressed[pos : (pos := pos + add_count * NIBBLE_SIZE)]
                chunk.extra = decompressed[pos:]

            chunks.append(chunk)

        self.data.offsets = offsets
        self.data.counts = counts
        self.data.uuid = uuids
        self.data.chunks = chunks
