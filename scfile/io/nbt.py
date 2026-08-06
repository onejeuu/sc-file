from collections.abc import Callable
from typing import ClassVar, Self

from scfile.core.content import DocumentValue
from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError
from scfile.formats.nbt.enums import Tag

from .base import StructReader


class NbtReader(StructReader):
    order: ByteOrder = ByteOrder.BIG

    _HANDLERS: ClassVar[dict[Tag, Callable[[Self], DocumentValue]]] = {
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
    ) -> DocumentValue:
        return self._HANDLERS[tag](self)

    def tag(
        self,
    ) -> Tag:
        try:
            return Tag(self.value(F.I8))

        except ValueError:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            ) from None

    def _byte_array(self) -> bytes:
        return self.read(self._length())

    def _list(self) -> list[DocumentValue]:
        tag = self.tag()
        length = self._length()
        return [self.parse(tag) for _ in range(length)]

    def _int_array(self) -> list[DocumentValue]:
        length = self._length()
        return [self.value(F.I32) for _ in range(length)]

    def _long_array(self) -> list[DocumentValue]:
        length = self._length()
        return [self.value(F.I64) for _ in range(length)]

    def _length(self) -> int:
        length = self.value(F.I32)
        if length < 0:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            )
        return length

    def _compound(self) -> dict[str, DocumentValue]:
        data = {}
        while True:
            tag = self.tag()
            if tag == Tag.END:
                break
            key = self.string(limit=None)
            data[key] = self.parse(tag)
        return data
