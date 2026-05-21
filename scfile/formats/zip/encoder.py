import zipfile

from scfile.core import FileEncoder, TexarrContent
from scfile.enums import ByteOrder, FileFormat


class TexarrEncoder(FileEncoder[TexarrContent]):
    format = FileFormat.ZIP
    order = ByteOrder.LITTLE

    def serialize(self):
        with zipfile.ZipFile(self, mode="w", compression=zipfile.ZIP_STORED) as zip:
            for path, data in self.data.textures:
                zip.writestr(path, data)
