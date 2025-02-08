from typing import Any

import numpy as np

from scfile import exceptions as exc
from scfile.consts import Factor, McsaModel, McsaSize
from scfile.enums import StructFormat as F
from scfile.geometry.mesh import BonesMapping
from scfile.io.streams import StructFileIO


# TODO: finally set proper numpy typing


def reshape(data: np.ndarray, size: int) -> list[list[Any]]:
    # tolist: no further manipulation is provided
    # and python works faster with native lists (for encoders)
    return data.reshape(-1, size).tolist()


def links(ids: np.ndarray, weights: np.ndarray, bones: BonesMapping) -> tuple[np.ndarray, np.ndarray]:
    # Convert local bone ids to skeleton bone ids
    ids = np.vectorize(bones.get)(ids)

    # Clean empty ids
    ids[weights == 0.0] = 0

    # Scale and Round
    weights = weights.astype(F.F32) / Factor.U8
    weights = weights.round(McsaModel.ROUND_DIGITS)

    # !!! TODO: weights normalize

    return (ids, weights)


class McsaFileIO(StructFileIO):
    def readstring(self):
        return self.reads().decode("utf-8", errors="replace")

    def readcount(self):
        count = self.readb(F.U32)

        if count > McsaModel.COUNT_LIMIT:
            raise exc.McsaCountsLimit(self.path, count)

        return count

    def readarray(self, fmt: str, count: int):
        data = self.unpack(f"{count}{fmt}")
        return np.array(data, dtype=np.dtype(fmt))

    def readdefault(self):
        # Read array
        data = self.readarray(fmt=F.F32, count=3)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        return reshape(data, 3)

    def readvertex(self, fmt: str, factor: float, size: int, count: int, scale: float = 1.0):
        # Read array
        data = self.readarray(fmt=fmt, count=count * size)

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
        data = self.readarray(fmt=fmt, count=count * size)

        return reshape(data, size)

    def readbonedata(self) -> list[float]:
        # Read vertex array
        data = self.readarray(fmt=F.F32, count=McsaSize.BONE)

        # TODO: fix type hints
        return data.tolist()  # type: ignore

    def readclipframes(self, count: int) -> list[list[list[float]]]:
        size = 7

        # Read array
        data = self.readarray(fmt=F.U16, count=count * size)

        # Scale values to floats
        data = data / (Factor.U16)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        # Reshape to arr[arr[float[3], float[4]]]
        data = data.reshape(-1, size)
        data = [[block[:3].tolist(), block[3:].tolist()] for block in data]

        # TODO: fix type hints
        return data  # type: ignore

    def readlinkspacked(self, count: int, bones: BonesMapping):
        size = 4

        # Read array
        data = self.readarray(fmt=F.U8, count=count * size)

        # Reshape to vertex[ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Parse Links
        ids, weights = links(data[:, 0, :], data[:, 1, :], bones)

        return (ids.tolist(), weights.tolist())

    def readlinksplains(self, count: int, bones: BonesMapping):
        size = 4

        # Read arrays
        ids = self.readarray(fmt=F.U8, count=count * size)
        weights = self.readarray(fmt=F.U8, count=count * size)

        # Parse Links
        ids, weights = links(ids, weights, bones)

        return (reshape(ids, size), reshape(weights, size))
