from scfile import formats
from scfile.core import FileDecoder, TexarrContent
from scfile.enums import ByteOrder, F, FileFormat


DELIMITER = ":"
FORMAT = FileFormat.DDS.suffix


class TexarrDecoder(FileDecoder[TexarrContent]):
    format = FileFormat.TEXARR
    order = ByteOrder.BIG

    _content = TexarrContent

    def to_zip(self):
        return self.convert_to(formats.zip.TexarrEncoder)

    def parse(self):
        self.data.count = self._readb(F.U32)

        for _ in range(self.data.count):
            self._parse_texture()

    def _parse_texture(self):
        path = self._readutf8().replace(DELIMITER, "/") + FORMAT
        size = self._readb(F.U32)
        texture = self.read(size)

        self.data.textures.append((path, texture))
