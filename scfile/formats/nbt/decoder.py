import gzip
import zlib
from typing import override

import zstandard as zstd

from scfile.consts import FormatSignature
from scfile.structures.content import DocumentContent
from scfile.core import Decoder
from scfile.enums import ByteOrder, FileFormat
from scfile.exceptions import BinaryStructureError
from scfile.io.nbt import NbtReader


class NbtDecoder(Decoder[DocumentContent]):
    format = FileFormat.NBT
    order = ByteOrder.LITTLE

    content_type = DocumentContent

    @override
    def _parse(self):
        data = self._decompress()

        with NbtReader(data, location=self.location) as reader:
            self.data.value = reader.document()

    def _decompress(self) -> bytes:
        data = self.io.read()

        try:
            if data.startswith(FormatSignature.GZIP):
                return gzip.decompress(data)

            if data.startswith(FormatSignature.ZSTD):
                return zstd.decompress(data)

        except (gzip.BadGzipFile, EOFError, zlib.error, zstd.ZstdError) as error:
            raise BinaryStructureError(
                location=self.location,
                offset=0,
            ) from error

        return data
