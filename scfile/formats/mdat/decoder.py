"""MDAT region decoder."""

from typing import override

import zstandard as zstd

from scfile.content import RegionContent
from scfile.content import regions as S
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.exceptions import BinaryStructureError, DecodingError

from . import payload
from .objects import objects
from .records import records
from .versions import CHUNK_HEADERS, REGION_KEY_BYTES, SUPPORTED_VERSIONS, Version


CHUNK_COUNT = 32 * 32
SECTOR_SIZE = 4096


class MdatDecoder(Decoder[RegionContent]):
    format = FileFormat.MDAT
    order = ByteOrder.BIG
    content_type = RegionContent

    @override
    def _parse(self) -> None:
        version = self.options.mdat_version or max(SUPPORTED_VERSIONS)
        if version not in SUPPORTED_VERSIONS:
            raise DecodingError(
                f"Unsupported MDAT version: {version}.",
                location=self.location,
            )

        region = self._read_table(version)
        table_end = self.io.tell()
        decompressor = zstd.ZstdDecompressor()

        for index, sector in enumerate(region.offsets):
            if not sector:
                continue

            chunk = self._read_chunk(
                index,
                sector,
                region.counts[index],
                table_end,
                version,
                decompressor,
            )
            region.chunks.append(chunk)

        self.data = region

    def _read_table(self, version: int) -> RegionContent:
        region = RegionContent(version=version)

        key_size = REGION_KEY_BYTES[version]
        if version == 7:
            keys = region.chunk_keys
        else:
            keys = region.uuids

        for _ in range(CHUNK_COUNT):
            sector, count = self.io.unpack(f"2{F.I32}")
            region.offsets.append(sector)
            region.counts.append(count)
            keys.append(self.io.read_exact(key_size))

        return region

    def _read_chunk(
        self,
        index: int,
        sector: int,
        count: int,
        table_end: int,
        version: int,
        decompressor: zstd.ZstdDecompressor,
    ) -> S.RegionChunk:
        start = sector * SECTOR_SIZE
        end = min(start + count * SECTOR_SIZE, self.io.size())

        if count <= 0 or start < table_end or end <= start:
            raise BinaryStructureError(location=self.location, offset=start)

        self.io.seek(start)
        header, header_raw = self._read_header(version, end)

        compressed, data = self._read_frame(
            header.compressed_size,
            end,
            decompressor,
        )

        sections = header.section_mask
        additions = header.add_mask
        if (
            sections & ~0xFFFF
            or additions & ~0xFFFF
            or additions & ~sections
            or len(data) < payload.required_size(sections, additions)
        ):
            raise BinaryStructureError(location=self.location, offset=start)

        chunk = payload.chunk(
            index,
            header,
            data,
            extended=self.options.extended_chunk,
        )
        chunk.header_raw = header_raw

        if self.options.extended_chunk:
            chunk.compressed = compressed
            chunk.record_list = records(chunk.records)

        if version in (6, 7):
            self._read_objects(chunk, version, end, decompressor)

        return chunk

    def _read_header(self, version: Version, end: int) -> tuple[S.ChunkHeader, bytes]:
        layout = CHUNK_HEADERS[version]
        start = self.io.tell()
        if start + layout.size > end:
            raise BinaryStructureError(location=self.location, offset=start)

        raw = self.io.read_exact(layout.size)
        values = layout.unpack(raw)
        match version:
            case 5 | 6:
                header = S.ChunkHeader(*values)
            case 7:
                length, key, sections, additions, terrain, compressed = values
                header = S.ChunkHeader(length, sections, additions, terrain, compressed, key)
            case _:
                raise DecodingError(f"Unsupported MDAT version: {version}.", location=self.location)
        return header, raw

    def _read_frame(
        self,
        size: int,
        end: int,
        decompressor: zstd.ZstdDecompressor,
    ) -> tuple[bytes, bytes]:
        start = self.io.tell()
        if size < 0 or start + size > end:
            raise BinaryStructureError(location=self.location, offset=start)

        compressed = self.io.read_exact(size)
        if not compressed:
            return b"", b""

        try:
            data = decompressor.decompress(compressed)
        except zstd.ZstdError as error:
            raise BinaryStructureError(location=self.location, offset=start) from error

        return compressed, data

    def _read_objects(
        self,
        chunk: S.RegionChunk,
        version: int,
        end: int,
        decompressor: zstd.ZstdDecompressor,
    ) -> None:
        if self.io.tell() + 4 > end:
            raise BinaryStructureError(location=self.location, offset=self.io.tell())

        size = self.io.value(F.I32)
        chunk.objects_size = size
        if size < 0 or self.io.tell() + size > end:
            raise BinaryStructureError(location=self.location, offset=self.io.tell())

        if not self.options.extended_chunk:
            self.io.skip(size)
            return

        compressed, data = self._read_frame(size, end, decompressor)
        chunk.objects_compressed = compressed
        chunk.objects_payload = data

        if data:
            chunk.objects = objects(data, version)
