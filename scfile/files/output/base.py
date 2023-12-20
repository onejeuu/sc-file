import struct
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any, Generic, List, Optional, TypeVar

from scfile.consts import PathLike
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as Format


class OutputData(ABC):
    """Can contain any type of data."""
    pass


T = TypeVar("T", bound="OutputData")


class BaseOutputFile(ABC, Generic[T]):
    DEFAULT_BYTEORDER = ByteOrder.LITTLE
    DEFAULT_FORMAT = Format.U32

    def __init__(
        self,
        path: PathLike,
        data: T,
        buffer: BytesIO,
    ):
        self.path = Path(path)
        self.data = data
        self.buffer = buffer

    magic: Optional[List[int]] = None
    """Magic value (signature) of output file. For example: `[0x89, 0x50, 0x4E, 0x47]`."""

    def create(self) -> bytes:
        """Create output file. Return output file bytes."""
        self.add_magic()
        self.write()
        return self.result

    @property
    def result(self) -> bytes:
        """Result bytes of conversion."""
        return self.buffer.getvalue()

    @abstractmethod
    def write(self) -> None:
        """Writes output file in buffer."""
        ...

    @property
    def filename(self) -> str:
        """Filename of output file."""
        return self.path.stem

    def add_magic(self):
        if self.magic:
            self._raw_write(bytes(self.magic))

    def _raw_write(self, data: bytes) -> None:
        self.buffer.write(data)

    def _write_null(self, count: int):
        self._raw_write(b'\x00' * 4 * count)

    def _write_str(self, *data: Any) -> None:
        string = "".join([str(i) for i in data])
        self.buffer.write(string.encode())

    def _write(
        self,
        v: Any,
        fmt: Format = DEFAULT_FORMAT,
        order: ByteOrder = DEFAULT_BYTEORDER
    ) -> None:
        data = struct.pack(f"{order}{fmt}", v)
        self.buffer.write(data)

    def __str__(self):
        return f"<{self.__class__.__name__}> frompath='{self.path.as_posix()}'"
