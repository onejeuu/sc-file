"""
Extends IOBase to support struct-based I/O.
"""

import io
import struct
from typing import Any, Optional

import numpy as np

from scfile.enums import ByteOrder, F, UnicodeErrors


class StructIO(io.IOBase):
    """Low-level binary I/O with structured packing/unpacking operations."""

    order: ByteOrder = ByteOrder.LITTLE
    unicode_errors: str = UnicodeErrors.REPLACE

    def _pack(self, fmt: str, *values: Any) -> bytes:
        return struct.pack(str(fmt), *values)

    def _unpack(self, fmt: str) -> tuple[Any, ...]:
        size = struct.calcsize(str(fmt))
        data = self.read(size)
        return struct.unpack(fmt, data)

    def _readarray(self, dtype: str, count: int, order: Optional[ByteOrder] = None):
        order = order or self.order
        datatype = np.dtype(f"{order}{dtype}")
        datasize = count * datatype.itemsize
        return np.frombuffer(self.read(datasize), dtype=datatype, count=count)

    def _readb(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        order = order or self.order
        return self._unpack(f"{order}{fmt}")[0]

    def _reads(self, prefix: str = F.U16, order: Optional[ByteOrder] = None) -> bytes:
        order = order or self.order
        size = self._readb(prefix, order)
        return self._unpack(f"{size}s")[0]

    def _readutf8(self) -> str:
        return self._reads().decode("utf-8", errors=self.unicode_errors)

    def _writeb(self, fmt: str, *values: Any, order: Optional[ByteOrder] = None) -> None:
        order = order or self.order
        data = self._pack(f"{order}{fmt}", *values)
        self.write(data)

    def _writenull(self, size: int = 4) -> None:
        self.write(bytes(size))

    def _writeutf8(self, string: str) -> None:
        self.write(string.encode("utf-8", errors=self.unicode_errors))
