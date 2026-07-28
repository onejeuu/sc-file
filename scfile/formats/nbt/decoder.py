import gzip

import zstandard as zstd

from scfile import formats
from scfile.core import FileDecoder, NbtContent
from scfile.enums import ByteOrder, FileFormat

from .enums import Tag
from scfile.io.nbt import NbtReader


class NbtDecoder(FileDecoder[NbtContent]):
    format = FileFormat.NBT
    order = ByteOrder.LITTLE

    content_factory = NbtContent

    def as_json(self):
        return self.convert_to(formats.json.JsonEncoder)

    def parse(self):
        data = self._decompress()
        reader = NbtReader(data, "rb", location=self.location)

        try:
            # Read root tag
            tag = reader.tag()
            if tag == Tag.END:
                return

            reader.string(limit=None)  # Skip name
            self.data.value = reader.parse(tag)

        finally:
            reader.close()

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
