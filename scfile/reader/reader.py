import io
import struct
from pathlib import Path
from typing import Any, Optional

from scfile.consts import McsaModel, Normalization, OlString, PathLike
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as Format
from scfile.exceptions import McsaCountsLimit


class BinaryReader(io.FileIO):
    DEFAULT_BYTEORDER = ByteOrder.STANDARD

    def __init__(self, path: PathLike, order: ByteOrder = DEFAULT_BYTEORDER):
        super().__init__(path, mode="rb")
        self.path = Path(path)
        self.order = order

    def readbin(self, fmt: str, order: Optional[ByteOrder] = None) -> Any:
        """Read binary value from stream."""

        order = order or self.order
        return self.unpack(f"{order}{fmt}")[0]

    def readstring(self, order: Optional[ByteOrder] = None) -> str:
        """Read an MCSA/OL file string from stream."""

        size = self.readbin(Format.U16, order)
        return self.unpack(f"{size}s")[0].decode()

    def readfourcc(self) -> bytes:
        """Read an OL file FourCC string from stream."""

        # read string and skip last 0x00 byte
        string = self.read(OlString.SIZE)[:-1]

        # xor byte if it's is not null
        return bytes(byte ^ OlString.XOR for byte in string if byte != OlString.NULL)

    def mcsa_counts(self):
        """Read MCSA counts from stream and validate against COUNT_LIMIT."""

        counts = self.readbin(Format.U32)
        if counts > McsaModel.COUNT_LIMIT:
            raise McsaCountsLimit(self.path, counts)
        return counts

    def mcsa_xyz(self, vertices_count: int):
        """Read MCSA vertices XYZ coordinates from stream."""

        fmt = Format.I16 * 3 + Format.U16

        return self._read_mcsa(fmt, vertices_count)

    def mcsa_uv(self, vertices_count: int):
        """Read MCSA vertices UV coordinates from stream."""

        fmt = Format.I16 * 2

        return self._read_mcsa(fmt, vertices_count)

    def mcsa_nrm(self, vertices_count: int):
        # TODO: docstring

        fmt = Format.I8 * 4

        return self._read_mcsa(fmt, vertices_count)

    def mcsa_polygons(self, polygons_count: int):
        """Read MCSA polygons from stream."""

        # If it works, dont touch it
        u32 = polygons_count * 3 >= Normalization.U16

        fmt = Format.U32 if u32 else Format.U16
        fmt *= 3

        return self._read_mcsa(fmt, polygons_count)

    def _read_mcsa(self, fmt: str, count: int):
        """Read MCSA data based on given format and count."""

        data = self._unpack_mcsa(fmt, count)
        return self._split_mcsa(fmt, data)

    def _unpack_mcsa(self, fmt: str, count: int):
        """Unpack MCSA data from stream."""

        fmt *= count
        return self.unpack(fmt)

    def _split_mcsa(self, fmt: str, data: Any):
        """Split MCSA data into an array of arrays."""

        size = len(fmt)
        return [
            data[i:i+size]
            for i in range(0, len(data), size)
        ]

    def unpack(self, fmt: str) -> Any:
        """Unpack binary data based on the given format."""

        size = struct.calcsize(str(fmt))
        data = self.read(size)
        return struct.unpack(fmt, data)
