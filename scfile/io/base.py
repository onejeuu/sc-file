import io
import struct
from typing import Any, Optional

from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F


class StructBufferedIOBase(io.BufferedIOBase):
    def unpack(self, fmt: str) -> Any:
        """Unpack binary data from buffer."""
        size = struct.calcsize(str(fmt))
        data = self.read(size)
        return struct.unpack(fmt, data)

    def pack(self, fmt: str, *v: Any) -> bytes:
        """Pack values into a bytes."""
        return struct.pack(str(fmt), *v)


class BinaryIO(StructBufferedIOBase):
    order = ByteOrder.LITTLE
    """Binary byte order."""

    def readb(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        """Unpack any binary data."""
        order = order or self.order
        return self.unpack(f"{order}{fmt}")[0]

    def reads(self, order: Optional[ByteOrder] = None) -> bytes:
        """Unpack length-prefixed string."""
        size = self.readb(F.U16, order)
        return self.unpack(f"{size}s")[0]

    def writeb(self, fmt: str, *v: Any, order: Optional[ByteOrder] = None) -> None:
        """Pack any binary data."""
        order = order or self.order
        data = self.pack(f"{order}{fmt}", *v)
        self.write(data)

    def writen(self, count: int = 1, size: int = 4) -> None:
        """Fill buffer with 4 bytes zeros."""
        self.write(bytes(size * count))

    def writes(self, string: str) -> None:
        """Write utf-8 encoded string."""
        self.write(string.encode("utf-8", errors="replace"))
