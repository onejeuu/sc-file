"""
Extensions for MS3D file format with custom struct-based I/O methods.
"""

from scfile.core.io import StructBytesIO
from scfile.enums import F

from .exceptions import Ms3dCountsLimit


class Ms3dFileIO(StructBytesIO):
    def _writecount(self, type: str, count: int, limit: int) -> None:
        if count > limit:
            raise Ms3dCountsLimit(type, count, limit)
        self._writeb(F.U16, count)

    def _writefixedstring(self, text: str) -> None:
        self.write(text.encode("utf-8").ljust(32, b"\x00"))
