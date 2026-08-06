"""NBT wire format reader and writer."""

from enum import IntEnum
from typing import assert_never

from scfile.core.content import DocumentValue
from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError

from .base import StructReader, StructWriter


class Tag(IntEnum):
    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10
    INT_ARRAY = 11
    LONG_ARRAY = 12

    def header(
        self,
        name: bytes = b"",
    ) -> bytes:
        """Encode a named NBT tag header."""

        return bytes((self,)) + len(name).to_bytes(2, "big") + name


class NbtReader(StructReader):
    order: ByteOrder = ByteOrder.BIG

    def document(self) -> DocumentValue:
        """Read one NBT document."""

        tag = self.tag()
        if tag == Tag.END:
            return None

        self.string(limit=None)  # Skip root name

        try:
            return self.parse(tag)

        except RecursionError as error:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            ) from error

    def tag(self) -> Tag:
        """Read one NBT tag type."""

        try:
            return Tag(self.value(F.I8))

        except ValueError:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            ) from None

    def parse(
        self,
        tag: Tag,
    ) -> DocumentValue:
        """Read the payload of a known NBT tag."""

        match tag:
            case Tag.END:
                return None
            case Tag.BYTE:
                return self.value(F.I8)
            case Tag.SHORT:
                return self.value(F.I16)
            case Tag.INT:
                return self.value(F.I32)
            case Tag.LONG:
                return self.value(F.I64)
            case Tag.FLOAT:
                return self.value(F.F32)
            case Tag.DOUBLE:
                return self.value(F.F64)
            case Tag.BYTE_ARRAY:
                return self._byte_array()
            case Tag.STRING:
                return self.string(limit=None)
            case Tag.LIST:
                return self._list()
            case Tag.COMPOUND:
                return self._compound()
            case Tag.INT_ARRAY:
                return self._int_array()
            case Tag.LONG_ARRAY:
                return self._long_array()
            case _:
                assert_never(tag)

    def _byte_array(self) -> bytes:
        return self.read_exact(self._length())

    def _list(self) -> list[DocumentValue]:
        tag = self.tag()
        return [self.parse(tag) for _ in range(self._length())]

    def _int_array(self) -> list[DocumentValue]:
        return self.array(F.I32, self._length()).tolist()

    def _long_array(self) -> list[DocumentValue]:
        return self.array(F.I64, self._length()).tolist()

    def _length(self) -> int:
        length = self.value(F.I32)
        if length < 0:
            raise BinaryStructureError(
                location=self.location,
                offset=self.tell(),
            )
        return length

    def _compound(self) -> dict[str, DocumentValue]:
        data: dict[str, DocumentValue] = {}

        while (tag := self.tag()) != Tag.END:
            name = self.string(limit=None)
            data[name] = self.parse(tag)

        return data


class NbtWriter(StructWriter):
    """Write NBT data to a binary stream."""

    order: ByteOrder = ByteOrder.BIG

    def tag(
        self,
        tag: Tag,
        name: bytes = b"",
    ) -> None:
        """Write a named NBT tag header."""

        self.write(tag.header(name))

    def list(
        self,
        tag: Tag,
        length: int,
    ) -> None:
        """Write an NBT list element type and length."""

        self.value(F.I8, tag)
        self.value(F.I32, length)

    def end(self) -> None:
        """Write an NBT compound terminator."""

        self.value(F.I8, Tag.END)
