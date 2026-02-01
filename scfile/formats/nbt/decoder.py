import gzip

import zstandard as zstd

from scfile.core import FileDecoder, NbtContent
from scfile.core.io import StructFileIO
from scfile.enums import ByteOrder, FileFormat

from .enums import Tag
from .io import NbtBytesIO


class NbtDecoder(FileDecoder[NbtContent], StructFileIO):
    format = FileFormat.NBT
    order = ByteOrder.LITTLE

    _content = NbtContent

    def to_json(self):
        from scfile.formats.json.encoder import JsonEncoder
        return self.convert_to(JsonEncoder)

    def parse(self):
        data = self._decompress()

        stream = NbtBytesIO(data)

        # Read root tag
        tag = stream._read_tag()
        if tag == Tag.END:
            return

        _ = stream._readutf8()  # Skip name
        self.data.value = stream._parse_tag(tag)

    def _decompress(self):
        data = self.read()

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
