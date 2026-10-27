"""Binary primitives used by MDAT."""

import struct

from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError

from .base import StructReader


class MdatReader(StructReader):
    order = ByteOrder.BIG

    def varuint(self) -> int:
        value = 0

        for shift in range(0, 35, 7):
            byte = self.read_exact(1)[0]
            if shift == 28 and byte & 0xF0:
                raise BinaryStructureError(location=self.location, offset=self.tell() - 1)

            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value

        raise BinaryStructureError(location=self.location, offset=self.tell())

    def java_utf(self) -> str:
        data = self.prefixed(F.U16)
        text = data.replace(b"\xc0\x80", b"\0").decode("utf-8", errors="surrogatepass")
        return text.encode("utf-16-be", errors="surrogatepass").decode("utf-16-be", errors="surrogatepass")

    def vector3(self) -> tuple[float, float, float]:
        return struct.unpack(">3f", self.read_exact(12))
