"""
Structured binary I/O.
"""

import os
import struct
from enum import IntEnum
from io import SEEK_CUR, SEEK_END, BytesIO, IOBase
from typing import IO, Any, Literal, Self, cast

import numpy as np
from numpy.typing import NDArray

from scfile.enums import ByteOrder, F, UnicodeErrors
from scfile.enums import SafetyLimit as Limit
from scfile.exceptions import BinaryStructureError, SafetyLimitError
from scfile.types import PathLike


type IOStream = PathLike | IOBase | bytes
type OutputStream = PathLike | IOBase
type FileMode = Literal["rb", "rb+", "wb", "wb+", "ab", "ab+"]


class StructIO:
    """Own a seekable binary stream used for structured I/O."""

    order: ByteOrder = ByteOrder.LITTLE
    """Default byte order."""

    errors: str = UnicodeErrors.REPLACE
    """UTF-8 error handling mode."""

    def __init__(
        self,
        stream: IOStream,
        mode: FileMode,
        order: ByteOrder | None = None,
        errors: str | None = None,
        location: str | None = None,
    ):
        """Open or take ownership of a seekable binary stream."""

        self.order = order or self.order
        self.errors = errors or self.errors

        if isinstance(stream, str | os.PathLike):
            path = os.fspath(stream)
            self._location = location or path
            self._stream = open(path, mode)
            return

        if isinstance(stream, bytes):
            self._stream = BytesIO(stream)
            self._location = location or f"<bytes at {hex(id(self._stream))}>"
            return

        if isinstance(stream, IOBase):
            self._stream = cast(IO[bytes], stream)
            name = getattr(self._stream, "name", None)
            fallback = f"<{type(stream).__name__} at {hex(id(stream))}>"
            self._location = location or (str(name) if name is not None else fallback)
            return

        raise TypeError(f"Expected IOStream, got {type(stream).__name__}")

    @property
    def stream(self) -> IO[bytes]:
        return self._stream

    @property
    def location(self) -> str:
        return self._location

    @property
    def closed(self) -> bool:
        return self._stream.closed

    def seek(
        self,
        position: int,
        whence: int = 0,
    ) -> int:
        return self._stream.seek(position, whence)

    def tell(self) -> int:
        return self._stream.tell()

    def size(self) -> int:
        position = self.tell()
        size = self.seek(0, SEEK_END)
        self.seek(position)
        return size

    def seekable(self) -> bool:
        return self._stream.seekable()

    def close(self) -> None:
        self._stream.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        *_,
    ) -> None:
        self.close()


class StructReader(StructIO):
    """Read structured values from a binary stream."""

    def read(
        self,
        size: int = -1,
    ) -> bytes:
        return self._stream.read(size)

    def skip(
        self,
        size: int,
    ) -> int:
        return self.seek(size, SEEK_CUR)

    def eof(self) -> bool:
        return self.tell() >= self.size()

    def readable(self) -> bool:
        return self._stream.readable()

    def read_exact(
        self,
        size: int,
    ) -> bytes:
        offset = self.tell()

        if size < 0:
            raise BinaryStructureError(
                location=self.location,
                offset=offset,
            )

        data = self.read(size)

        if len(data) != size:
            raise BinaryStructureError(
                location=self.location,
                offset=offset,
            )

        return data

    def unpack(
        self,
        fmt: str,
        order: ByteOrder | None = None,
    ) -> tuple[Any, ...]:
        """Read and unpack structured values."""

        try:
            order = order or self.order
            fmt = f"{order}{fmt}"
            size = struct.calcsize(fmt)
            return struct.unpack(fmt, self.read_exact(size))

        except struct.error:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            ) from None

    def value(
        self,
        fmt: str,
        order: ByteOrder | None = None,
    ) -> Any:
        """Read one structured value."""

        return self.unpack(fmt, order)[0]

    def array(
        self,
        dtype: str,
        count: int,
        order: ByteOrder | None = None,
    ) -> NDArray[Any]:
        """Read a NumPy array."""

        order = order or self.order
        datatype = np.dtype(f"{order}{dtype}")
        size = count * datatype.itemsize
        return np.frombuffer(self.read_exact(size), dtype=datatype, count=count)

    def string(
        self,
        prefix: str = F.U16,
        order: ByteOrder | None = None,
        limit: IntEnum | None = Limit.STRING,
    ) -> str:
        """Read a length-prefixed UTF-8 string."""

        data = self.prefixed(prefix, order, limit)
        return data.decode("utf-8", errors=self.errors)

    def prefixed(
        self,
        prefix: str = F.U16,
        order: ByteOrder | None = None,
        limit: IntEnum | None = None,
    ) -> bytes:
        """Read length-prefixed bytes."""

        size = self.value(prefix, order)
        if limit is not None:
            self.check(size, limit)
        return self.unpack(f"{size}s")[0]

    def count(
        self,
        fmt: str,
        limit: IntEnum,
    ) -> int:
        """Read and validate a bounded count."""

        return self.check(self.value(fmt), limit)

    def check(
        self,
        value: int,
        limit: IntEnum,
    ) -> int:
        """Validate a decoded count."""

        if value < 0:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            )

        maximum = int(limit)
        if value > maximum:
            raise SafetyLimitError(
                limit.name.lower(),
                value,
                maximum,
                location=self.location,
                offset=self.tell(),
            )
        return value


class StructWriter(StructIO):
    """Write structured values to a binary stream."""

    def write(
        self,
        data: bytes,
    ) -> int:
        return self._stream.write(data)

    def writable(self) -> bool:
        return self._stream.writable()

    def flush(self) -> None:
        self._stream.flush()

    def to_bytes(self) -> bytes:
        """Return all bytes written to the stream."""

        if isinstance(self._stream, BytesIO):
            return self._stream.getvalue()

        self.flush()
        position = self.tell()

        try:
            self.seek(0)
            return self._stream.read()

        finally:
            self.seek(position)

    def pack(
        self,
        fmt: str,
        *values: Any,
        order: ByteOrder | None = None,
    ) -> bytes:
        """Pack structured values."""

        order = order or self.order
        return struct.pack(f"{order}{fmt}", *values)

    def value(
        self,
        fmt: str,
        *values: Any,
        order: ByteOrder | None = None,
    ) -> None:
        """Write structured values."""

        self.write(self.pack(fmt, *values, order=order))

    def null(
        self,
        size: int = 4,
    ) -> None:
        """Write null bytes."""

        self.write(bytes(size))

    def string(
        self,
        string: str,
    ) -> None:
        """Write a UTF-8 string."""

        self.write(string.encode("utf-8", errors=self.errors))
