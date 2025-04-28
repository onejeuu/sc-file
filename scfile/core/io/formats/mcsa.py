from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from scfile import exceptions as exc
from scfile.consts import Factor, McsaModel, McsaSize
from scfile.core.io.streams import StructFileIO
from scfile.enums import StructFormat as F
from scfile.geometry.mesh import BonesMapping


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

    # Scale, Round
    weights = weights.astype(F.F32) / Factor.U8
    weights = weights.round(McsaModel.ROUND_DIGITS)
    # TODO: Normalize

    return (ids, weights)


class McsaFileIO(StructFileIO):
    def readstring(self) -> str:
        return self.reads().decode("utf-8", errors="replace")

    def readcount(self) -> int:
        count = self.readb(F.U32)

        if count > McsaModel.COUNT_LIMIT:
            raise exc.McsaCountsLimit(self.path, count)

        return count

    def readarray(self, fmt: str, count: int) -> NDArray[Any]:
        data = self.unpack(f"{count}{fmt}")
        return np.array(data, dtype=np.dtype(fmt))

    def readdefault(self) -> list[list[float]]:
        size = McsaSize.DEFAULTS

        # Read array
        data = self.readarray(fmt=F.F32, count=size)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        return reshape(data, size)

    def readvertex(self, fmt: str, factor: float, size: int, count: int, scale: float = 1.0) -> list[list[float]]:
        # Read array
        data = self.readarray(fmt=fmt, count=count * size)

        # Scale values to floats
        data = data * scale / (factor)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        return reshape(data, size)

    def readpolygons(self, count: int) -> list[list[int]]:
        size = McsaSize.POLYGONS

        # Validate that indexes fits into U16 range. Otherwise use U32.
        indexes = count * size
        fmt = F.U16 if indexes <= Factor.U16 else F.U32

        # Read array
        data = self.readarray(fmt=fmt, count=count * size)

        return reshape(data, size)

    def readbonedata(self) -> list[float]:
        # TODO: read pos and rot one time
        # Read array
        data: NDArray[np.float64] = self.readarray(fmt=F.F32, count=McsaSize.BONE)

        return cast(list[float], data.tolist())

    def readcliptransforms(self) -> Any:
        # ! WIP
        size = McsaSize.CLIP_FRAMES

        # Read array
        data = self.readarray(fmt=F.U16, count=size)

        # Scale values to floats
        data = data / (Factor.U16 - 1)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        # Reshape to arr[arr[float[4], float[3]]]
        sub = 3
        data = [data[:sub].tolist(), data[sub:].tolist()]

        # TODO: fix typing
        return data  # type: ignore

    def readclipframes(self, count: int) -> list[list[list[float]]]:
        # ! WIP
        size = McsaSize.CLIP_FRAMES

        # Read array
        data = self.readarray(fmt=F.U16, count=count * size)

        # Scale values to floats
        data = data / (Factor.U16)

        # Round digits
        data = data.round(McsaModel.ROUND_DIGITS)

        # Reshape to arr[arr[float[4], float[3]]]
        data = data.reshape(-1, size)
        data = [[block[:4].tolist(), block[4:].tolist()] for block in data]

        # TODO: fix typing
        return data  # type: ignore

    def readlinkspacked(self, count: int, bones: BonesMapping) -> tuple[list[int], list[float]]:
        size = 4

        # Read array
        data = self.readarray(fmt=F.U8, count=count * size)

        # Reshape to vertex[ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Parse Links
        ids, weights = links(data[:, 0, :], data[:, 1, :], bones)

        # TODO: fix typing
        return (ids.tolist(), weights.tolist())  # type: ignore

    def readlinksplains(self, count: int, bones: BonesMapping) -> tuple[list[list[int]], list[list[float]]]:
        size = 4

        # Read arrays
        ids = self.readarray(fmt=F.U8, count=count * size)
        weights = self.readarray(fmt=F.U8, count=count * size)

        # Parse Links
        ids, weights = links(ids, weights, bones)

        return (reshape(ids, size), reshape(weights, size))
