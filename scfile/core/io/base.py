"""
Extends IOBase to support struct-based I/O.
"""

import io
import struct
from typing import Any, Optional

from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.enums import UnicodeErrors


class StructIO(io.IOBase):
    order: ByteOrder = ByteOrder.LITTLE
    unicode_errors: str = UnicodeErrors.REPLACE

    def pack(self, fmt: str, *values: Any) -> bytes:
        return struct.pack(str(fmt), *values)

    def unpack(self, fmt: str) -> tuple[Any, ...]:
        size = struct.calcsize(str(fmt))
        data = self.read(size)
        return struct.unpack(fmt, data)

    def readb(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        order = order or self.order
        return self.unpack(f"{order}{fmt}")[0]

    def reads(self, prefix: str = F.U16, order: Optional[ByteOrder] = None) -> bytes:
        order = order or self.order
        size = self.readb(prefix, order)
        return self.unpack(f"{size}s")[0]

    def readutf8(self) -> str:
        return self.reads().decode("utf-8", errors=self.unicode_errors)

    def writeb(self, fmt: str, *values: Any, order: Optional[ByteOrder] = None) -> None:
        order = order or self.order
        data = self.pack(f"{order}{fmt}", *values)
        self.write(data)

    def writenull(self, size: int = 4) -> None:
        self.write(bytes(size))

    def writeutf8(self, string: str) -> None:
        self.write(string.encode("utf-8", errors=self.unicode_errors))
