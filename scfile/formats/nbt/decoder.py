import gzip
from typing import override

import zstandard as zstd

from scfile import formats
from scfile.core import Decoder, DocumentContent
from scfile.enums import ByteOrder, FileFormat
from scfile.io.nbt import NbtReader

from .enums import Tag


class NbtDecoder(Decoder[DocumentContent]):
    format = FileFormat.NBT
    order = ByteOrder.LITTLE

    content_type = DocumentContent

    def as_json(self):
        return self.convert_to(formats.json.JsonEncoder)

    @override
    def _parse(self):
        data = self._decompress()
        with NbtReader(data, "rb", location=self.location) as reader:
            # Read root tag
            tag = reader.tag()
            if tag == Tag.END:
                return

            reader.string(limit=None)  # Skip name
            self.data.value = reader.parse(tag)

    def _decompress(self):
        data = self.io.read()

        try:
            # Gzip is standard nbt compression
            data = gzip.decompress(data)

        except Exception:
            try:
                # Some synced configs use zstd
                data = zstd.decompress(data)

            except Exception:
                pass

        return data
