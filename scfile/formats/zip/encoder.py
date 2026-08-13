import zipfile
from typing import override

from scfile.core import Encoder
from scfile.enums import ByteOrder, FileFormat
from scfile.structures.content import ArchiveContent


class ZipEncoder(Encoder[ArchiveContent]):
    format = FileFormat.ZIP
    order = ByteOrder.LITTLE

    content_type = ArchiveContent

    @override
    def _serialize(self):
        with zipfile.ZipFile(self.io, mode="w", compression=zipfile.ZIP_STORED) as archive:
            for path, data in self.data.entries:
                archive.writestr(path, data)
