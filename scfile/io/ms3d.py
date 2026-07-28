"""
Extensions for MS3D file format with custom struct-based I/O methods.
"""

from scfile.enums import F
from scfile.exceptions import Ms3dCapacityError

from .base import StructWriter


class Ms3dWriter(StructWriter):
    def count(
        self,
        subject: str,
        count: int,
        limit: int,
    ) -> None:
        if count > limit:
            raise Ms3dCapacityError(subject, count, limit)
        self.value(F.U16, count)

    def fixed_string(
        self,
        text: str,
    ) -> None:
        self.write(text.encode("utf-8").ljust(32, b"\x00"))
