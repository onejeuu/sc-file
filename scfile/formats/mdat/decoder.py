import struct
from typing import override

from zstandard import ZstdDecompressor, ZstdError

from scfile.content import RegionContent
from scfile.content import regions as S
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.exceptions import BinaryStructureError, MdatVersionError
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
        if version not in SUPPORTED_VERSIONS:
            raise MdatVersionError(version, location=self.location)

        self.data.version = version
        self._ctx["zstd"] = ZstdDecompressor()

        match version:
            case 5 | 6:
                entry_format = ">ii16s"

            case 7:
                entry_format = ">ii8s"

        table = self.io.read_exact(CHUNK_COUNT * struct.calcsize(entry_format))

        for index, (sector, _, _) in enumerate(struct.iter_unpack(entry_format, table)):
            if not sector:
                continue

            self.io.seek(sector * SECTOR_SIZE)

            match version:
                case 5 | 6:
                    header = S.ChunkHeader(*struct.unpack(">5i", self.io.read_exact(20)))

                case 7:
                    length, key, sections, additions, terrain, size = struct.unpack(">i8s4i", self.io.read_exact(28))
                    header = S.ChunkHeader(length, sections, additions, terrain, size, key)

            self.data.chunks.append(self._parse_chunk(index, header))

    def _parse_chunk(self, index: int, header: S.ChunkHeader) -> S.RegionChunk:
        data = self._parse_compressed(header.compressed_size)
        chunk = payload.chunk(
            index,
            header,
            data,
            objects=self.options.mdat_objects,
            materials=self.options.mdat_materials,
        )

        if self.data.version >= 6:
            self._parse_chunk_objects(chunk)

        return chunk

    def _parse_chunk_objects(self, chunk: S.RegionChunk) -> None:
        size = self.io.value(F.I32)

        if not self.options.mdat_objects:
            self.io.skip(size)
            return

        if size:
            data = self._parse_compressed(size)
            chunk.objects = objects(data, self.data.version)

    def _parse_compressed(self, size: int) -> bytes:
        offset = self.io.tell()
        compressed = self.io.read_exact(size)
        zstd = self._ctx["zstd"]

        try:
            return zstd.decompress(compressed)

        except ZstdError as error:
            raise BinaryStructureError(location=self.location, offset=offset) from error
