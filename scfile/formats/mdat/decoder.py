"""MDAT region decoder."""

import struct
from typing import override

import zstandard as zstd

from scfile.content import RegionContent
from scfile.content import regions as S
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.exceptions import BinaryStructureError, DecodingError
from scfile.io.mdat import MdatReader

from . import payload
from .objects import objects
from .versions import SUPPORTED_VERSIONS


CHUNK_COUNT = 32 * 32
SECTOR_SIZE = 4096


class MdatDecoder(Decoder[RegionContent, MdatReader]):
    format = FileFormat.MDAT
    order = ByteOrder.BIG
    io_factory = MdatReader
    content_type = RegionContent

    @override
    def _parse(self) -> None:
        version = self.options.mdat_version or max(SUPPORTED_VERSIONS)
        # TODO: custom exception?
        if version not in SUPPORTED_VERSIONS:
            raise DecodingError(f"Unsupported MDAT version: {version}.", location=self.location)

        self.data.version = version
        match version:
            case 5:
                self._parse_v5()
            case 6:
                self._parse_v6()
            case 7:
                self._parse_v7()

    def _parse_v5(self) -> None:
        table = self.io.read_exact(CHUNK_COUNT * 24)
        table_end = self.io.tell()
        file_size = self.io.size()
        decompressor = zstd.ZstdDecompressor()

        for index, (sector, count, _) in enumerate(struct.iter_unpack(">ii16s", table)):
            if not sector:
                continue

            start = sector * SECTOR_SIZE
            end = min(start + count * SECTOR_SIZE, file_size)
            if count <= 0 or start < table_end or end <= start:
                raise BinaryStructureError(location=self.location, offset=start)

            self.io.seek(start)
            self.data.chunks.append(self._parse_chunk(index, end, decompressor))

    def _parse_v6(self) -> None:
        table = self.io.read_exact(CHUNK_COUNT * 24)
        table_end = self.io.tell()
        file_size = self.io.size()
        decompressor = zstd.ZstdDecompressor()

        for index, (sector, count, _) in enumerate(struct.iter_unpack(">ii16s", table)):
            if not sector:
                continue

            start = sector * SECTOR_SIZE
            end = min(start + count * SECTOR_SIZE, file_size)
            if count <= 0 or start < table_end or end <= start:
                raise BinaryStructureError(location=self.location, offset=start)

            self.io.seek(start)
            self.data.chunks.append(self._parse_chunk(index, end, decompressor))

    def _parse_v7(self) -> None:
        table = self.io.read_exact(CHUNK_COUNT * 16)
        table_end = self.io.tell()
        file_size = self.io.size()
        decompressor = zstd.ZstdDecompressor()

        for index, (sector, count, _) in enumerate(struct.iter_unpack(">ii8s", table)):
            if not sector:
                continue

            start = sector * SECTOR_SIZE
            end = min(start + count * SECTOR_SIZE, file_size)
            if count <= 0 or start < table_end or end <= start:
                raise BinaryStructureError(location=self.location, offset=start)

            self.io.seek(start)
            self.data.chunks.append(self._parse_chunk(index, end, decompressor))

    def _parse_chunk(
        self,
        index: int,
        end: int,
        decompressor: zstd.ZstdDecompressor,
    ) -> S.RegionChunk:
        start = self.io.tell()

        match self.data.version:
            case 5 | 6:
                if start + 20 > end:
                    raise BinaryStructureError(location=self.location, offset=start)

                raw = self.io.read_exact(20)
                header = S.ChunkHeader(*struct.unpack(">5i", raw))

            case 7:
                if start + 28 > end:
                    raise BinaryStructureError(location=self.location, offset=start)

                raw = self.io.read_exact(28)
                length, key, sections, additions, terrain, size = struct.unpack(">i8s4i", raw)
                header = S.ChunkHeader(length, sections, additions, terrain, size, key)

            case _:
                raise DecodingError(
                    f"Unsupported MDAT version: {self.data.version}.",
                    location=self.location,
                    offset=start,
                )

        offset = self.io.tell()
        size = header.compressed_size
        if size < 0 or offset + size > end:
            raise BinaryStructureError(location=self.location, offset=offset)

        compressed = self.io.read_exact(size)
        data = b""
        try:
            if compressed:
                data = decompressor.decompress(compressed)
        except zstd.ZstdError as error:
            raise BinaryStructureError(location=self.location, offset=offset) from error

        if header.section_mask & ~0xFFFF or header.add_mask & ~0xFFFF or header.add_mask & ~header.section_mask:
            raise BinaryStructureError(location=self.location, offset=start)

        required_size = (
            header.section_mask.bit_count() * (payload.SECTION_SIZE + 4 * payload.NIBBLE_SIZE)
            + header.add_mask.bit_count() * payload.NIBBLE_SIZE
            + payload.BIOME_SIZE
        )
        if len(data) < required_size:
            raise BinaryStructureError(location=self.location, offset=start)

        chunk = payload.chunk(index, header, data, extended=self.options.extended_chunk)

        if self.data.version >= 6:
            offset = self.io.tell()
            if offset + 4 > end:
                raise BinaryStructureError(location=self.location, offset=offset)

            size = self.io.value(F.I32)
            offset = self.io.tell()
            if size < 0 or offset + size > end:
                raise BinaryStructureError(location=self.location, offset=offset)

            if not self.options.extended_chunk:
                self.io.skip(size)
                return chunk

            compressed_objects = self.io.read_exact(size)
            if compressed_objects:
                try:
                    object_data = decompressor.decompress(compressed_objects)

                except zstd.ZstdError as error:
                    raise BinaryStructureError(location=self.location, offset=offset) from error

                chunk.objects = objects(object_data, self.data.version)

        return chunk
