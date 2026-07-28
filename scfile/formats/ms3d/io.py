"""
Extensions for MS3D file format with custom struct-based I/O methods.
"""

from scfile.core import StructWriter
from scfile.enums import F

from .exceptions import Ms3dCapacityError


class Ms3dWriter(StructWriter):
    def write_count(
        self,
        type: str,
        count: int,
        limit: int,
    ) -> None:
        if count > limit:
            raise Ms3dCapacityError(type, count, limit)
        self.value(F.U16, count)

    def write_fixed_string(
        self,
        text: str,
    ) -> None:
        self.write(text.encode("utf-8").ljust(32, b"\x00"))
