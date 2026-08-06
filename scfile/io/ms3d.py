"""
Extensions for MS3D file format with custom struct-based I/O methods.
"""

from scfile.enums import F
from scfile.exceptions import Ms3dCapacityError

from .base import StructWriter


STRING_SIZE = 32


class Ms3dWriter(StructWriter):
    def check(
        self,
        subject: str,
        count: int,
        limit: int,
    ) -> None:
        if count > limit:
            raise Ms3dCapacityError(
                subject,
                count,
                limit,
                location=self.location,
            )

    def count(
        self,
        subject: str,
        count: int,
        limit: int,
    ) -> None:
        self.check(subject, count, limit)
        self.value(F.U16, count)

    def fixed_string(
        self,
        text: str,
    ) -> None:
        data = text.encode("utf-8")
        self.check("string bytes", len(data), STRING_SIZE)
        self.write(data.ljust(STRING_SIZE, b"\x00"))
