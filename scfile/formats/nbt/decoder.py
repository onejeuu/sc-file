import gzip
import zlib
from typing import override

import zstandard as zstd

from scfile.core import Decoder, DocumentContent
from scfile.enums import ByteOrder, FileFormat
from scfile.exceptions import BinaryStructureError
from scfile.io.nbt import NbtReader

from .enums import Tag


GZIP_MAGIC = b"\x1f\x8b"
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


class NbtDecoder(Decoder[DocumentContent]):
    format = FileFormat.NBT
    order = ByteOrder.LITTLE

    content_type = DocumentContent

    @override
    def _parse(self):
        data = self._decompress()

        with NbtReader(data, location=self.location) as reader:
            # Read root tag
            tag = reader.tag()
            if tag == Tag.END:
                return

            reader.string(limit=None)  # Skip name
            self.data.value = reader.parse(tag)

    def _decompress(self) -> bytes:
        data = self.io.read()

        try:
            if data.startswith(GZIP_MAGIC):
                return gzip.decompress(data)

            if data.startswith(ZSTD_MAGIC):
                return zstd.decompress(data)

        except (gzip.BadGzipFile, EOFError, zlib.error, zstd.ZstdError) as error:
            raise BinaryStructureError(
                location=self.location,
                offset=0,
            ) from error

        return data
