from typing import Callable, TypeAlias

from scfile.core.context.content import NbtValue
from scfile.core.io import StructBytesIO
from scfile.enums import ByteOrder, F

from .enums import Tag


Handler: TypeAlias = Callable[[], NbtValue]


class NbtBytesIO(StructBytesIO):
    order: ByteOrder = ByteOrder.BIG

    def _parse_tag(self, tag: Tag) -> NbtValue:
        handlers: dict[Tag, Handler] = {
            Tag.END: lambda: None,
            Tag.BYTE: lambda: self._readb(F.I8),
            Tag.SHORT: lambda: self._readb(F.I16),
            Tag.INT: lambda: self._readb(F.I32),
            Tag.LONG: lambda: self._readb(F.I64),
            Tag.FLOAT: lambda: self._readb(F.F32),
            Tag.DOUBLE: lambda: self._readb(F.F64),
            Tag.BYTE_ARRAY: self._read_byte_array,
            Tag.STRING: self._readutf8,
            Tag.LIST: self._read_list,
            Tag.COMPOUND: self._read_compound,
            Tag.INT_ARRAY: self._read_int_array,
            Tag.LONG_ARRAY: self._read_long_array,
        }
        return handlers[tag]()

    def _read_tag(self) -> Tag:
        return Tag(self._readb(F.I8))

    def _read_byte_array(self) -> bytes:
        length = self._readb(F.I32)
        return self.read(length)

    def _read_list(self) -> list[NbtValue]:
        tag = self._read_tag()
        length = self._readb(F.I32)
        return [self._parse_tag(tag) for _ in range(length)]

    def _read_int_array(self) -> list[int]:
        length = self._readb(F.I32)
        return [self._readb(F.I32) for _ in range(length)]

    def _read_long_array(self) -> list[int]:
        length = self._readb(F.I32)
        return [self._readb(F.I64) for _ in range(length)]

    def _read_compound(self) -> dict[str, NbtValue]:
        data = {}
        while True:
            tag = self._read_tag()
            if tag == Tag.END:
                break
            key = self._readutf8()
            data[key] = self._parse_tag(tag)
        return data
