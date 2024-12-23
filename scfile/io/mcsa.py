from typing import Any

import numpy as np
from numpy.typing import NDArray

from scfile.consts import Factor, McsaModel, McsaSize
from scfile.enums import StructFormat as F
from scfile.io.file import StructFileIO


def reshape(data: NDArray[Any], size: int) -> list[list[Any]]:
    # tolist: no further manipulation is provided
    # and python works faster with native lists (for encoders)
    return data.reshape(-1, size).tolist()


class McsaFileIO(StructFileIO):
    def readstring(self):
        return self.reads().decode("utf-8", errors="replace")

    def readcount(self):
        count = self.readb(F.U32)

        if count > McsaModel.COUNT_LIMIT:
            raise Exception(f"Count limit {count:,} > {McsaModel.COUNT_LIMIT:,}")

        return count

    def readarray(self, fmt: str, size: int, count: int):
        data = self.unpack(f"{size*count}{fmt}")
        return np.array(data, dtype=np.dtype(fmt))

    def readvertex(self, fmt: str, factor: float, size: int, count: int, scale: float = 1.0):
        # Read array
        data = self.readarray(fmt=fmt, size=size, count=count)

        # Scale values to floats
        data = data * scale / (factor)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        return reshape(data, size)

    def readpolygons(self, count: int):
        size = McsaSize.POLYGONS

        # Validate that indexes fits into U16 range. Otherwise use U32.
        indexes = count * size
        fmt = F.U16 if indexes <= Factor.U16 else F.U32

        # Read array
        data = self.readarray(fmt=fmt, size=size, count=count)

        return reshape(data, size)

    def readbonedata(self) -> list[int]:
        # Read vertex array
        data = self.readarray(fmt=F.F32, size=McsaSize.BONE, count=1)

        # TODO: fix type hints
        return data.tolist()  # type: ignore

    def readlinkspacked(self, count: int):
        # Read array
        data = self.readarray(fmt=F.U8, size=4, count=count)

        # Reshape to vertex[ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Bone ids
        ids = data[:, 0, :]

        # Scale weights to floats
        weights = data[:, 1, :] / Factor.U8

        # Round digits
        weights = weights.round(McsaModel.ROUND_DIGITS)

        return (ids.tolist(), weights.tolist())

    def _readlinksids(self, count: int):
        # Read array
        size = 4
        data = self.readarray(fmt=F.U8, size=size, count=count)

        return reshape(data, size)

    def _readlinksweights(self, count: int):
        # Read array
        size = 4
        data = self.readarray(fmt=F.U8, size=size, count=count)

        # Scale weights to floats
        data = data / Factor.U8

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        return reshape(data, size)

    def readlinksplains(self, count: int):
        # Read data
        ids = self._readlinksids(count)
        weights = self._readlinksweights(count)

        return (ids, weights)
