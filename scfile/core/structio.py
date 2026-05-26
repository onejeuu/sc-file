"""
Low-level binary I/O with structured packing and unpacking operations.

Provides a base class for reading and writing binary data in various formats
using :mod:`struct` and :mod:`numpy`. Designed to be subclassed by format-specific I/O classes.
"""

import io
import struct
from typing import Any, Optional

import numpy as np

from scfile.enums import ByteOrder, F, UnicodeErrors


class StructIO(io.IOBase):
    """
    Base class for structured binary I/O.

    Extends :class:`io.IOBase` with methods for packed binary operations.
    Subclasses must implement :class:`io.IOBase` interface.
    """

    order: ByteOrder = ByteOrder.LITTLE
    """Default byte order for pack/unpack operations."""

    unicode_errors: str = UnicodeErrors.REPLACE
    """Error handling mode for UTF-8 encoding/decoding."""

    def _pack(self, fmt: str, *values: Any) -> bytes:
        """Serialize *values* to bytes."""

        return struct.pack(str(fmt), *values)

    def _unpack(self, fmt: str) -> tuple[Any, ...]:
        """Deserialize bytes."""

        size = struct.calcsize(str(fmt))
        data = self.read(size)
        return struct.unpack(fmt, data)

    def _readarray(self, dtype: str, count: int, order: Optional[ByteOrder] = None):
        """Read an array of *count* elements of type *dtype*."""

        order = order or self.order
        datatype = np.dtype(f"{order}{dtype}")
        datasize = count * datatype.itemsize
        return np.frombuffer(self.read(datasize), dtype=datatype, count=count)

    def _readb(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        """Read single primitive value."""

        order = order or self.order
        return self._unpack(f"{order}{fmt}")[0]

    def _reads(self, prefix: str = F.U16, order: Optional[ByteOrder] = None) -> bytes:
        """Read length prefixed string."""

        order = order or self.order
        size = self._readb(prefix, order)
        return self._unpack(f"{size}s")[0]

    def _readutf8(self, prefix: str = F.U16, order: Optional[ByteOrder] = None) -> str:
        """Read a length prefixed UTF-8 string."""

        return self._reads(prefix=prefix, order=order).decode("utf-8", errors=self.unicode_errors)

    def _writeb(self, fmt: str, *values: Any, order: Optional[ByteOrder] = None) -> None:
        """Serialize and write *values*."""

        order = order or self.order
        data = self._pack(f"{order}{fmt}", *values)
        self.write(data)

    def _writenull(self, size: int = 4) -> None:
        """Write *size* null bytes."""

        self.write(bytes(size))

    def _writeutf8(self, string: str) -> None:
        """Write UTF-8 encoded *string*."""

        self.write(string.encode("utf-8", errors=self.unicode_errors))
