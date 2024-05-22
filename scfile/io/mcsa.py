from typing import Any, Dict

import numpy as np
from numpy.typing import NDArray

from scfile.consts import Factor, McsaModel, McsaSize
from scfile.enums import StructFormat as F
from scfile.exceptions.mcsa import McsaCountsLimit

from .binary import BinaryFileIO


class McsaFileIO(BinaryFileIO):
    FLOATS_ROUND = 6

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
        data = data * scale / (factor)

        # Round digits
        data = data.round(self.FLOATS_ROUND)

        return self._reshape(data, size)

    def readpolygons(self, count: int):
        """Read vertex indexes."""
        size = McsaSize.POLYGONS

        # Validate that indexes fits into U16 range. Otherwise use U32.
        indexes = count * size
        fmt = F.U16 if indexes < Factor.U16 else F.U32

        # Read array
        data = self.readarray(fmt=fmt, size=size, count=count)

        return self._reshape(data, size)

    def _boneids_to_global(self, data: Any, mesh_bones: Dict[int, int]):
        def apply_mesh_bones(x: int):
            return mesh_bones.get(x, McsaModel.ROOT_BONE_ID)

        vectorized = np.vectorize(apply_mesh_bones)

        return vectorized(data)

    def readlinkspacked(self, count: int, mesh_bones: Dict[int, int]):
        # Read array
        data = self.readarray(fmt=F.U8, size=4, count=count)

        # Reshape to vertex[ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Convert mesh bone ids to global skeleton ids
        ids = self._boneids_to_global(data[..., 0], mesh_bones)

        # Scale weights to floats
        weights = data[..., 1] / Factor.U8

        # Round digits
        weights = weights.round(self.FLOATS_ROUND)

        return (ids.tolist(), weights.tolist())

    def _readlinksids(self, count: int, mesh_bones: Dict[int, int]):
        # Read array
        size = 4
        data = self.readarray(fmt=F.U8, size=size, count=count)

        # Convert mesh bone ids to global skeleton ids
        data = self._boneids_to_global(data, mesh_bones)

        return self._reshape(data, size)

    def _readlinksweights(self, count: int):
        # Read array
        size = 4
        data = self.readarray(fmt=F.U8, size=size, count=count)

        # Scale weights to floats
        data = data / Factor.U8

        # Round digits
        data = data.round(self.FLOATS_ROUND)

        return self._reshape(data, size)

    def readlinksplains(self, count: int, mesh_bones: Dict[int, int]):
        ids = self._readlinksids(count=count, mesh_bones=mesh_bones)
        weights = self._readlinksweights(count=count)
        return (ids, weights)

    def _reshape(self, data: NDArray[Any], size: int) -> list[list[Any]]:
        """Reshapes array to list of lists."""
        # tolist: no further manipulation is provided
        # and python works faster with native lists (for encoders)
        return data.reshape(-1, size).tolist()
