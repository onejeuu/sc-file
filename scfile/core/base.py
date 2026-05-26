"""
Binary stream adapter for file-like sources.

Wraps any binary source (file path, bytes, or IO stream)
into a unified interface for reading and writing structured binary data.
"""

import io
import os
import struct
from abc import ABC
from io import BytesIO, IOBase
from pathlib import Path
from typing import IO, Any, BinaryIO, Literal, Optional, TypeAlias, cast

from scfile.enums import FileFormat
from scfile.exceptions import InvalidStructureError
from scfile.types import PathLike

from .options import Options
from .structio import StructIO


IOStream: TypeAlias = str | bytes | PathLike | BinaryIO
FileMode: TypeAlias = Literal["rb", "rb+", "wb", "wb+", "ab", "ab+"]
TempContext: TypeAlias = dict[str, Any]


class BaseFile(StructIO, ABC):
    """Unified binary stream handler."""

    format: FileFormat = FileFormat.NONE
    """Associated file format."""

    signature: Optional[bytes] = None
    """Expected file signature."""

    options: Options
    """Shared handlers options."""

    _stream: IO[bytes]

    def __init__(
        self,
        stream: IOStream,
        mode: FileMode = "rb",
    ):
        """
        Args:
            stream: Source input. File path, bytes, or binary IO stream.
            mode: File mode (binary) for opening when ``stream`` is path.
        """

        if isinstance(stream, (str, Path)):
            self._stream = open(os.fspath(stream), mode)

        elif isinstance(stream, bytes):
            self._stream = BytesIO(stream)

        elif isinstance(stream, IOBase):
            self._stream = cast(IO[bytes], stream)

        else:
            raise TypeError(f"Expected IOStream, got {type(stream).__name__}")

        self.ctx: TempContext = {}

    @property
    def suffix(self) -> str:
        return self.format.suffix

    @property
    def location(self) -> str:
        return repr(self._stream)

    @property
    def closed(self) -> bool:
        return self._stream.closed

    def size(self) -> int:
        current = self.tell()
        self.seek(0, 2)
        size = self.tell()
        self.seek(current)
        return size

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def write(self, data: bytes) -> int:
        return self._stream.write(data)

    def seek(self, pos: int, whence: int = 0) -> int:
        return self._stream.seek(pos, whence)

    def skip(self, size: int):
        self.seek(size, io.SEEK_CUR)

    def tell(self) -> int:
        return self._stream.tell()

    def readable(self) -> bool:
        return self._stream.readable()

    def writable(self) -> bool:
        return self._stream.writable()

    def seekable(self) -> bool:
        return self._stream.seekable()

    def flush(self) -> None:
        self._stream.flush()

    def close(self) -> None:
        self.ctx = {}
        self._stream.close()

    def getvalue(self) -> bytes:
        if isinstance(self._stream, BytesIO):
            return self._stream.getvalue()
        current = self.tell()
        self.seek(0)
        data = self.read()
        self.seek(current)
        return data

    def is_eof(self) -> bool:
        return self.size() <= self.tell()

    def _unpack(self, fmt: str) -> tuple[Any, ...]:
        try:
            return super()._unpack(fmt)

        except struct.error:
            raise InvalidStructureError(self.location, position=self.tell())

    def __repr__(self) -> str:
        closed = "closed" if self.closed else "open"
        return f"<{type(self).__name__} {self.location} [{closed}]>"
