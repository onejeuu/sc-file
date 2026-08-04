import zipfile
from typing import override

from scfile.core import Encoder, TexarrContent
from scfile.enums import ByteOrder, FileFormat


class TexarrEncoder(Encoder[TexarrContent]):
    content_type = TexarrContent
    format = FileFormat.ZIP
    order = ByteOrder.LITTLE

    @override
    def _serialize(self):
        with zipfile.ZipFile(self.io, mode="w", compression=zipfile.ZIP_STORED) as zip:
            for path, data in self.data.textures:
                zip.writestr(path, data)
