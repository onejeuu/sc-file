from typing import override

from scfile import formats
from scfile.core import FileDecoder, TexarrContent
from scfile.enums import ByteOrder, F, FileFormat


DELIMITER = ":"
FORMAT = FileFormat.DDS.suffix


class TexarrDecoder(FileDecoder[TexarrContent]):
    format = FileFormat.TEXARR
    order = ByteOrder.BIG

    content_type = TexarrContent

    def as_zip(self):
        return self.convert_to(formats.zip.TexarrEncoder)

    @override
    def _parse(self):
        self.data.count = self.io.value(F.U32)

        for _ in range(self.data.count):
            self._parse_texture()

    def _parse_texture(self):
        path = self.io.string().replace(DELIMITER, "/") + FORMAT
        size = self.io.value(F.U32)
        texture = self.io.read(size)

        self.data.textures.append((path, texture))
