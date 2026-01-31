from typing import Callable, ClassVar, Self

from scfile.core.context.content import NbtValue
from scfile.core.io import StructBytesIO
from scfile.enums import ByteOrder, F

from .enums import Tag


class NbtBytesIO(StructBytesIO):
    order: ByteOrder = ByteOrder.BIG

    _HANDLERS: ClassVar[dict[Tag, Callable[[Self], NbtValue]]] = {
        Tag.END: lambda _: None,
        Tag.BYTE: lambda s: s._readb(F.I8),
        Tag.SHORT: lambda s: s._readb(F.I16),
        Tag.INT: lambda s: s._readb(F.I32),
        Tag.LONG: lambda s: s._readb(F.I64),
        Tag.FLOAT: lambda s: s._readb(F.F32),
        Tag.DOUBLE: lambda s: s._readb(F.F64),
        Tag.BYTE_ARRAY: lambda s: s._read_byte_array(),
        Tag.STRING: lambda s: s._readutf8(),
        Tag.LIST: lambda s: s._read_list(),
        Tag.COMPOUND: lambda s: s._read_compound(),
        Tag.INT_ARRAY: lambda s: s._read_int_array(),
        Tag.LONG_ARRAY: lambda s: s._read_long_array(),
    }

    def _parse_tag(self, tag: Tag) -> NbtValue:
        return self._HANDLERS[tag](self)

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
