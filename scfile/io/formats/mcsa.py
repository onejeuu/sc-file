from typing import Any

import numpy as np
from numpy.typing import NDArray

from scfile import exceptions as exc
from scfile.consts import Factor, McsaModel, McsaSize
from scfile.enums import StructFormat as F
from scfile.io.streams import StructFileIO


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
            raise exc.McsaCountsLimit(self.path, count)

        return count

    def readarray(self, fmt: str, size: int, count: int):
        data = self.unpack(f"{size * count}{fmt}")
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

    def readbonedata(self) -> list[float]:
        # Read vertex array
        data = self.readarray(fmt=F.F32, size=McsaSize.BONE, count=1)

        # TODO: fix type hints
        return data.tolist()  # type: ignore

    def readanimframes(self, count: int) -> list[list[list[float]]]:
        size = 7

        # Read array
        data = self.readarray(fmt=F.U16, size=size, count=count)

        # Scale values to floats
        data = data / (Factor.U16)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        # Reshape to arr[arr[float[3], float[4]]]
        data = data.reshape(-1, size)
        data = [[block[:3].tolist(), block[3:].tolist()] for block in data]

        # TODO: fix type hints
        return data  # type: ignore

    def _boneids_to_global(self, data: Any, bones: dict[int, int]):
        def apply_mesh_bones(x: int):
            return bones.get(x, McsaModel.ROOT_BONE_ID)

        vectorized = np.vectorize(apply_mesh_bones)

        return vectorized(data)

    def readlinkspacked(self, count: int, max_links: int, bones: dict[int, int]):
        # Read array
        data = self.readarray(fmt=F.U8, size=4, count=count)

        # Reshape to vertex[ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Bone ids
        ids = data[:, 0, :max_links]

        # Convert mesh bone ids to global skeleton ids
        ids = self._boneids_to_global(ids, bones)

        # Scale weights to floats
        weights = data[:, 1, :] / Factor.U8

        # Round digits
        weights = weights.round(McsaModel.ROUND_DIGITS)

        return (ids.tolist(), weights.tolist())

    def _readlinksids(self, count: int, bones: dict[int, int]):
        # Read array
        size = 4
        ids = self.readarray(fmt=F.U8, size=size, count=count)

        # Convert mesh bone ids to global skeleton ids
        ids = self._boneids_to_global(ids, bones)

        return reshape(ids, size)

    def _readlinksweights(self, count: int):
        # Read array
        size = 4
        weights = self.readarray(fmt=F.U8, size=size, count=count)

        # Scale weights to floats
        weights = weights / Factor.U8

        # Round digits
        weights = weights.round(McsaModel.ROUND_DIGITS)

        return reshape(weights, size)

    def readlinksplains(self, count: int, max_links: int, bones: dict[int, int]):
        # Read data
        ids = self._readlinksids(count, bones)
        weights = self._readlinksweights(count)

        return (ids, weights)
