import os
import struct
from abc import ABC
from io import BytesIO, IOBase
from pathlib import Path
from typing import IO, Any, BinaryIO, Literal, Optional, TypeAlias, cast

from scfile.enums import FileFormat
from scfile.exceptions import InvalidStructureError
from scfile.types import PathLike

from .options import UserOptions
from .structio import StructIO


IOStream: TypeAlias = str | bytes | PathLike | BinaryIO
FileMode: TypeAlias = Literal["rb", "rb+", "wb", "wb+", "ab", "ab+"]


class BaseFile(StructIO, ABC):
    format: FileFormat = FileFormat.NONE

    signature: Optional[bytes] = None
    options: UserOptions

    _stream: IO[bytes]

    def __init__(self, stream: IOStream, mode: FileMode = "rb"):
        if isinstance(stream, (str, Path)):
            self._stream = open(os.fspath(stream), mode)

        elif isinstance(stream, bytes):
            self._stream = BytesIO(stream)

        elif isinstance(stream, IOBase):
            self._stream = cast(IO[bytes], stream)

        else:
            raise TypeError(f"Expected IOStream, got {type(stream).__name__}")

    @property
    def suffix(self) -> str:
        return self.format.suffix

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def write(self, data: bytes) -> int:
        return self._stream.write(data)

    def seek(self, pos: int, whence: int = 0) -> int:
        return self._stream.seek(pos, whence)

    def tell(self) -> int:
        return self._stream.tell()

    def readable(self) -> bool:
        return self._stream.readable()

    def writable(self) -> bool:
        return self._stream.writable()

    def seekable(self) -> bool:
        return self._stream.seekable()

    @property
    def closed(self) -> bool:
        return self._stream.closed

    def close(self) -> None:
        self._stream.close()

    def flush(self) -> None:
        self._stream.flush()

    def getvalue(self) -> bytes:
        if isinstance(self._stream, BytesIO):
            return self._stream.getvalue()
        current = self.tell()
        self.seek(0)
        data = self.read()
        self.seek(current)
        return data

    @property
    def location(self) -> str:
        return repr(self._stream)

    @property
    def size(self) -> int:
        current = self.tell()
        self.seek(0, 2)
        size = self.tell()
        self.seek(current)
        return size

    def is_eof(self) -> bool:
        return self.size <= self.tell()

    def _unpack(self, fmt: str) -> tuple[Any, ...]:
        try:
            return super()._unpack(fmt)

        except struct.error as err:
            raise InvalidStructureError(self.location, position=self.tell()) from err

    def __repr__(self) -> str:
        closed = "closed" if self.closed else "open"
        return f"<{type(self).__name__} {self.location} [{closed}]>"
