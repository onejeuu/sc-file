import struct
from enum import Enum
from io import BufferedReader
from typing import Any, Optional

from scfile import exceptions as exc


class ByteOrder(Enum):
    BIG = ">"
    LITTLE = "<"


class BinaryFileReader:
    DEFAULT_ORDER = ByteOrder.BIG

    def __init__(self, buffer: BufferedReader) -> None:
        self._buffer = buffer
        self.order = self.DEFAULT_ORDER

    def read(self, size: Optional[int] = None) -> bytes:
        return self._buffer.read(size)

    def tell(self):
        return self._buffer.tell()

    def byte(self, order: Optional[ByteOrder] = None) -> int:
        return self._unpack("b", 1, order)

    def bigbyte(self, order: Optional[ByteOrder] = None) -> int:
        return self._unpack("B", 1, order)

    def sword(self, order: Optional[ByteOrder] = None) -> int:
        return self._unpack("h", 2, order)

    def uword(self, order: Optional[ByteOrder] = None) -> int:
        return self._unpack("H", 2, order)

    def sdword(self, order: Optional[ByteOrder] = None) -> int:
        return self._unpack("i", 4, order)

    def udword(self, order: Optional[ByteOrder] = None) -> int:
        return self._unpack("I", 4, order)

    def float(self, order: Optional[ByteOrder] = None) -> float:
        return self._unpack("f", 4, order)

    def _unpack(self, fmt: str, size: int, order: Optional[ByteOrder]) -> Any:
        order = order or self.order
        return struct.unpack(f"{order.value}{fmt}", self.read(size))[0]

    def zstring(self) -> str:
        """zero-end string"""

        result = ""

        while True:
            byte = self._buffer.read(1)
            if byte == b"\x00":
                break
            result += byte.decode()

        return result

    def mcsastring(self):
        """mcsa file string"""

        try:
            result = ""
            length = self.uword(ByteOrder.LITTLE)

            for _ in range(length):
                result += chr(self.byte())

        except Exception as err:
            raise exc.McsaStringError(err)

        return result
