from abc import ABC, abstractmethod
from typing import Callable, ClassVar

import zstandard as zstd

from scfile.content import RegionContent
from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import BinaryStructureError
from scfile.io.base import StructReader
from scfile.options import Options

from . import payload
from .objects import objects
from .records import records


CHUNK_COUNT = 32 * 32
SECTOR_SIZE = 4 * 1024


class RegionDecoder(ABC):
    version: ClassVar[int]
    key_size: ClassVar[int]
    header_size: ClassVar[int]
    object_header: ClassVar[Callable[[StructReader], S.ObjectHeader] | None] = None

    def __init__(self, reader: StructReader, options: Options):
        self.io = reader
        self.options = options
        self.zctx = zstd.ZstdDecompressor()

    @abstractmethod
    def header(self) -> S.ChunkHeader: ...

    def read(self) -> RegionContent:
        result = RegionContent(version=self.version)
        keys: list[bytes] = []
        for _ in range(CHUNK_COUNT):
            sector, count = self.io.unpack(f"2{F.I32}")
            result.offsets.append(sector)
            result.counts.append(count)
            keys.append(self.io.read_exact(self.key_size))
        if self.key_size == 16:
            result.uuids = keys
        else:
            result.chunk_keys = keys
        for index, sector in enumerate(result.offsets):
            if sector:
                result.chunks.append(self.chunk(index, sector, result.counts[index]))
        return result

    def frame(self, size: int, end: int) -> tuple[bytes, bytes]:
        start = self.io.tell()
        if size < 0 or start + size > end:
            raise BinaryStructureError(location=self.io.location, offset=start)
        compressed = self.io.read_exact(size)
        if not compressed:
            return b"", b""
        try:
            data = self.zctx.decompress(compressed)
        except zstd.ZstdError as error:
            raise BinaryStructureError(location=self.io.location, offset=start) from error
        return compressed, data

    def chunk(self, index: int, sector: int, count: int) -> S.RegionChunk:
        start = sector * SECTOR_SIZE
        end = min(start + count * SECTOR_SIZE, self.io.size())
        table_size = CHUNK_COUNT * (8 + self.key_size)
        if start < table_size or count <= 0 or start + self.header_size > end:
            raise BinaryStructureError(location=self.io.location, offset=start)
        self.io.seek(start)
        header_raw = self.io.read_exact(self.header_size)
        self.io.seek(start)
        header = self.header()
        compressed, data = self.frame(header.compressed_size, end)
        result = payload.chunk(index, header, data, extended=self.options.extended_chunk)
        result.header_raw = header_raw
        if self.options.extended_chunk:
            result.compressed = compressed
            result.record_list = records(result.records)
        object_header = type(self).object_header
        if object_header is not None:
            if self.io.tell() + 4 > end:
                raise BinaryStructureError(location=self.io.location, offset=self.io.tell())
            header.objects_size = self.io.value(F.I32)
            if self.options.extended_chunk:
                compressed_objects, object_data = self.frame(header.objects_size, end)
                result.objects_compressed = compressed_objects
                result.objects_payload = object_data
                if object_data:
                    result.objects = objects(object_data, object_header)
            else:
                if header.objects_size < 0 or self.io.tell() + header.objects_size > end:
                    raise BinaryStructureError(location=self.io.location, offset=self.io.tell())
                self.io.skip(header.objects_size)
        return result
