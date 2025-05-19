"""
Extensions for MS3D file format with custom struct-based I/O methods.
"""

from scfile.core.io.streams import StructBytesIO
from scfile.enums import StructFormat as F

from .exceptions import Ms3dCountsLimit


class Ms3dFileIO(StructBytesIO):
    def writecount(self, type: str, count: int, limit: int) -> None:
        if count > limit:
            raise Ms3dCountsLimit(type, count, limit)
        self.writeb(F.U16, count)
