import struct
from io import FileIO
from pathlib import Path
from typing import Any, Optional

from scfile.consts import McsaModel, Normalization, OlString, PathLike
from scfile.exceptions import McsaCountsLimit

from .enums import ByteOrder, Format


class BinaryReader(FileIO):
    DEFAULT_BYTEORDER = ByteOrder.STANDARD

    def __init__(self, path: PathLike, order: ByteOrder = DEFAULT_BYTEORDER):
        super().__init__(path, mode="rb")
        self.path = Path(path)
        self.order = order

    def i8(self, order: Optional[ByteOrder] = None) -> int:
        """`signed byte` `1 byte`"""
        return self._unpack(Format.I8, order)

    def i16(self, order: Optional[ByteOrder] = None) -> int:
        """`signed short` `word` `2 bytes`"""
        return self._unpack(Format.I16, order)

    def i32(self, order: Optional[ByteOrder] = None) -> int:
        """`signed integer` `double word` `4 bytes`"""
        return self._unpack(Format.I32, order)

    def i64(self, order: Optional[ByteOrder] = None) -> int:
        """`signed long` `quad word` `8 bytes`"""
        return self._unpack(Format.I64, order)

    def u8(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned byte` `1 byte`"""
        return self._unpack(Format.U8, order)

    def u16(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned short` `word` `2 bytes`"""
        return self._unpack(Format.U16, order)

    def u32(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned integer` `double word` `4 bytes`"""
        return self._unpack(Format.U32, order)

    def u64(self, order: Optional[ByteOrder] = None) -> int:
        """`unsigned long` `quad word` `8 bytes`"""
        return self._unpack(Format.U64, order)

    def f16(self, order: Optional[ByteOrder] = None) -> float:
        """`float` `half-precision` `2 bytes`"""
        return self._unpack(Format.F16, order)

    def f32(self, order: Optional[ByteOrder] = None) -> float:
        """`float` `single-precision` `4 bytes`"""
        return self._unpack(Format.F32, order)

    def f64(self, order: Optional[ByteOrder] = None) -> float:
        """`float` `double-precision` `8 bytes`"""
        return self._unpack(Format.F64, order)

    def string_mcsa(self) -> bytes:
        """mcsa file string"""

        size = self.u16(ByteOrder.LITTLE)
        return bytes(
            self.u8()
            for _ in range(size)
        )

    def string_ol_fourcc(self) -> bytes:
        """ol file fourcc string"""

        # and skip last 0x00 byte
        return bytes(
            char ^ OlString.XOR
            for char in self.read(OlString.SIZE)[:-1]
            if char != OlString.NULL
        )

    def string_ol_id(self) -> bytes:
        """ol file id string"""

        size = self.u16()
        return bytes(
            self.u8()
            for _ in range(size)
        )

    def mcsa_counts(self):
        counts = self.u32()
        if counts > McsaModel.COUNT_LIMIT:
            raise McsaCountsLimit(self.path, counts)
        return counts

    def mcsa_xyz(self, vertices_count: int):
        fmt = Format.I16 * 3 + Format.U16

        return self._read_mcsa_data(fmt, vertices_count)

    def mcsa_uv(self, vertices_count: int):
        fmt = Format.I16 * 2

        return self._read_mcsa_data(fmt, vertices_count)

    def mcsa_polygons(self, polygons_count: int):
        # If it works, dont touch it
        u32 = polygons_count * 3 >= Normalization.U16

        fmt = Format.U32 if u32 else Format.U16
        fmt *= 3

        return self._read_mcsa_data(fmt, polygons_count)

    def _read_mcsa_data(self, fmt: str, count: int):
        data = self._unpack_mcsa_data(fmt, count)
        return self._split_mcsa_data(fmt, data)

    def _unpack_mcsa_data(self, fmt: str, count: int):
        fmt *= count
        size = self._calcsize(fmt)
        return self._raw_unpack(fmt, size)

    def _split_mcsa_data(self, fmt: str, data: Any):
        size = len(fmt)
        return [
            data[i:i+size]
            for i in range(0, len(data), size)
        ]

    def _calcsize(self, fmt: str) -> int:
        return struct.calcsize(str(fmt))

    def _raw_unpack(self, fmt: str, size: int) -> Any:
        data = self.read(size)
        return struct.unpack(fmt, data)

    def _unpack(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        order = order or self.order
        size = self._calcsize(fmt)
        return self._raw_unpack(f"{order}{fmt}", size)[0]
