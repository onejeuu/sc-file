import zipfile

from scfile.core import FileEncoder, TextureArrayContent
from scfile.enums import FileFormat


class TextureArrayEncoder(FileEncoder[TextureArrayContent]):
    format = FileFormat.ZIP

    def serialize(self):
        with zipfile.ZipFile(self, mode="w", compression=zipfile.ZIP_STORED) as zip:
            for path, data in self.data.textures:
                zip.writestr(path, data)
