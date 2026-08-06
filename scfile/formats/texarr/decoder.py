from typing import override

from scfile.core import ArchiveContent, Decoder
from scfile.enums import ByteOrder, F, FileFormat


DELIMITER = ":"
SUFFIX = ".dds"


class TexarrDecoder(Decoder[ArchiveContent]):
    format = FileFormat.TEXARR
    order = ByteOrder.BIG

    content_type = ArchiveContent

    @override
    def _parse(self):
        count = self.io.value(F.U32)
        self._ctx["COUNT_ENTRIES"] = count

        for _ in range(count):
            self._parse_texture()

    def _parse_texture(self):
        path = self.io.string().replace(DELIMITER, "/") + SUFFIX
        size = self.io.value(F.U32)
        texture = self.io.read(size)

        self.data.entries.append((path, texture))
