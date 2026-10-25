import struct
from typing import Any
from uuid import UUID


class Reader:
    def __init__(self, data: memoryview):
        self.data = data
        self.offset = 0

    def unpack(self, format: str) -> tuple[Any, ...]:
        size = struct.calcsize(format)
        if self.offset + size > len(self.data):
            raise EOFError(f"Need {size} bytes at {self.offset}; {len(self.data) - self.offset} available")
        values = struct.unpack_from(format, self.data, self.offset)
        self.offset += size
        return values

    def number(self, format: str) -> int:
        return int(self.unpack(format)[0])

    def numbers(self, format: str, count: int) -> tuple[int, ...]:
        if count < 0:
            raise EOFError(f"Negative element count at {self.offset}")
        return tuple(int(value) for value in self.unpack(f">{count}{format}"))

    def floats(self, count: int) -> tuple[float, ...]:
        if count < 0:
            raise EOFError(f"Negative element count at {self.offset}")
        return tuple(float(value) for value in self.unpack(f">{count}f"))

    def vector(self) -> tuple[float, float, float]:
        x, y, z = self.floats(3)
        return x, y, z

    def bytes(self, size: int) -> memoryview:
        start = self.offset
        self.skip(size)
        return self.data[start : self.offset]

    def uuid(self) -> UUID:
        return UUID(bytes=self.bytes(16).tobytes())

    def utf(self) -> str:
        raw = self.bytes(self.number(">H")).tobytes()
        text = raw.replace(b"\xc0\x80", b"\0").decode("utf-8", errors="surrogatepass")
        return text.encode("utf-16-be", errors="surrogatepass").decode("utf-16-be", errors="surrogatepass")

    def varint(self) -> int:
        value = 0
        for shift in range(0, 35, 7):
            byte = self.number(">B")
            if shift == 28 and byte & 0xF0:
                raise EOFError(f"VarInt exceeds uint32 at {self.offset - 1}")
            value |= (byte & 127) << shift
            if byte < 128:
                return value
        raise EOFError("VarInt exceeds five bytes")

    def skip(self, size: int) -> None:
        if size < 0 or self.offset + size > len(self.data):
            raise EOFError(f"Need {size} bytes at {self.offset}; {len(self.data) - self.offset} available")
        self.offset += size
