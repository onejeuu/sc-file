import struct
from io import FileIO
from pathlib import Path
from typing import Any, Optional

from .enums import ByteOrder, Format, OlString


class BinaryReader(FileIO):
    DEFAULT_BYTEORDER = ByteOrder.STANDARD

    def __init__(
        self,
        path: str | Path,
        order: ByteOrder = DEFAULT_BYTEORDER
    ):
        super().__init__(path, mode="rb")
        self.path = Path(path)
        self.order = order

    def i8(self, order: Optional[ByteOrder] = None) -> int:
        """`signed byte` `1 byte`"""
        return self.unpack(Format.I8, order)

    def i16(self, order: Optional[ByteOrder] = None) -> int:
        """`signed short` `word` `2 bytes`"""
        return self.unpack(Format.I16, order)

    def i32(self, order: Optional[ByteOrder] = None) -> int:
        """`signed integer` `double word` `4 bytes`"""
        return self.unpack(Format.I32, order)

    def i64(self, order: Optional[ByteOrder] = None) -> int:
        """`signed long` `quad word` `8 bytes`"""
        return self.unpack(Format.I64, order)

    def u8(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned byte` `1 byte`"""
        return self.unpack(Format.U8, order)

    def u16(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned short` `word` `2 bytes`"""
        return self.unpack(Format.U16, order)

    def u32(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned integer` `double word` `4 bytes`"""
        return self.unpack(Format.U32, order)

    def u64(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned long` `quad word` `8 bytes`"""
        return self.unpack(Format.U64, order)

    def f16(self, order: Optional[ByteOrder] = None) -> float:
        """`float` `half-precision` `2 bytes`"""
        return self.unpack(Format.F16, order)

    def f32(self, order: Optional[ByteOrder] = None) -> float:
        """`float` `single-precision` `4 bytes`"""
        return self.unpack(Format.F32, order)

    def f64(self, order: Optional[ByteOrder] = None) -> float:
        """`float` `double-precision` `8 bytes`"""
        return self.unpack(Format.F64, order)

    def mcsa_string(self) -> bytes:
        """mcsa file string"""

        size = self.u16(ByteOrder.LITTLE)
        return bytes(
            self.i8()
            for _ in range(size)
        )

    def ol_fourcc_string(self, size: int = OlString.SIZE) -> bytes:
        """ol file fourcc string"""

        return bytes(
            char ^ OlString.XOR
            for char in self.read(size)
            if char != OlString.NULL
        )

    def ol_id_string(self, id_size: int):
        """ol file id string"""

        return bytes(
            self.i8()
            for _ in range(id_size)
        )

    def raw_unpack(self, fmt: str, size: int) -> Any:
        data = self.read(size)
        return struct.unpack(fmt, data)

    def unpack(self, fmt: Format | str, order: Optional[ByteOrder] = None) -> Any:
        order = order or self.order
        size = struct.calcsize(str(fmt))
        return self.raw_unpack(f"{order}{fmt}", size)[0]
