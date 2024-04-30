from typing import Any

import numpy as np
from numpy.typing import NDArray

from scfile.consts import Factor, McsaModel, McsaSize
from scfile.enums import StructFormat as F
from scfile.exceptions.mcsa import McsaCountsLimit
from scfile.io.binary import BinaryFileIO


class McsaFileIO(BinaryFileIO):
    def readstring(self) -> str:
        """Read length-prefixed utf-8 string."""
        return self.reads().decode("utf-8", errors="replace")

    def readcounts(self):
        """Read unsigned int and validates count limit."""
        counts = self.readb(F.U32)
        if counts > McsaModel.COUNT_LIMIT:
            raise McsaCountsLimit(self.path, counts)
        return counts

    def readarray(self, fmt: str, size: int, count: int):
        """Read repetitive data values."""
        data = self.unpack(f"{size*count}{fmt}")
        return np.array(data, dtype=np.dtype(fmt))

    def readvertex(self, fmt: str, factor: float, size: int, count: int, scale: float = 1.0):
        """Read vertex data and scale it to floats."""
        # Read array
        data = self.readarray(fmt=fmt, size=size, count=count)

        # Scale values to floats
        data = data * scale / factor

        return self._reshape(data, size)

    def readpolygons(self, count: int):
        """Read vertex indexes and shift it to +1."""
        size = McsaSize.POLYGONS

        # Validate that indexes fits into U16 range. Otherwise use U32.
        indexes = count * size
        fmt = F.U16 if indexes < Factor.U16 else F.U32

        # Read array
        data = self.readarray(fmt=fmt, size=size, count=count)

        return self._reshape(data, size)

    def _reshape(self, data: NDArray[Any], size: int) -> list[list[Any]]:
        """Reshapes array to list of lists."""
        # tolist: no further manipulation is provided
        # and python works faster with native lists (for encoders)
        return data.reshape(-1, size).tolist()
