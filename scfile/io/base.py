import io
import struct
from typing import Any, Optional

from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F


class StructIOBase(io.IOBase):
    order = ByteOrder.LITTLE

    def pack(self, fmt: str, *values: Any) -> bytes:
        return struct.pack(str(fmt), *values)

    def unpack(self, fmt: str) -> tuple[Any]:
        size = struct.calcsize(str(fmt))
        data = self.read(size)

        if size != len(data):
            raise Exception(f"Not enough bytes. {size} needed, {len(data)} readed.")

        return struct.unpack(fmt, data)


class StructIO(StructIOBase):
    def readb(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        order = order or self.order

        return self.unpack(f"{order}{fmt}")[0]

    def reads(self, order: Optional[ByteOrder] = None) -> bytes:
        order = order or self.order

        size = self.readb(F.U16, order)
        return self.unpack(f"{size}s")[0]

    def writeb(self, fmt: str, *values: Any, order: Optional[ByteOrder] = None) -> None:
        order = order or self.order

        data = self.pack(f"{order}{fmt}", *values)
        self.write(data)

    def writenull(self, count: int = 1, size: int = 4) -> None:
        self.write(bytes(size * count))

    def writeutf8(self, string: str) -> None:
        self.write(string.encode("utf-8", errors="replace"))
