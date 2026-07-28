from typing import Callable, ClassVar, Self

from scfile.core.content import NbtValue
from scfile.enums import ByteOrder, F
from scfile.formats.nbt.enums import Tag

from .base import StructReader


class NbtReader(StructReader):
    order: ByteOrder = ByteOrder.BIG

    _HANDLERS: ClassVar[dict[Tag, Callable[[Self], NbtValue]]] = {
        Tag.END: lambda _: None,
        Tag.BYTE: lambda s: s.value(F.I8),
        Tag.SHORT: lambda s: s.value(F.I16),
        Tag.INT: lambda s: s.value(F.I32),
        Tag.LONG: lambda s: s.value(F.I64),
        Tag.FLOAT: lambda s: s.value(F.F32),
        Tag.DOUBLE: lambda s: s.value(F.F64),
        Tag.BYTE_ARRAY: lambda s: s._byte_array(),
        Tag.STRING: lambda s: s.string(limit=None),
        Tag.LIST: lambda s: s._list(),
        Tag.COMPOUND: lambda s: s._compound(),
        Tag.INT_ARRAY: lambda s: s._int_array(),
        Tag.LONG_ARRAY: lambda s: s._long_array(),
    }

    def parse(
        self,
        tag: Tag,
    ) -> NbtValue:
        return self._HANDLERS[tag](self)

    def tag(self) -> Tag:
        return Tag(self.value(F.I8))

    def _byte_array(self) -> bytes:
        length = self.value(F.I32)
        return self.read(length)

    def _list(self) -> list[NbtValue]:
        tag = self.tag()
        length = self.value(F.I32)
        return [self.parse(tag) for _ in range(length)]

    def _int_array(self) -> list[int]:
        length = self.value(F.I32)
        return [self.value(F.I32) for _ in range(length)]

    def _long_array(self) -> list[int]:
        length = self.value(F.I32)
        return [self.value(F.I64) for _ in range(length)]

    def _compound(self) -> dict[str, NbtValue]:
        data = {}
        while True:
            tag = self.tag()
            if tag == Tag.END:
                break
            key = self.string(limit=None)
            data[key] = self.parse(tag)
        return data
