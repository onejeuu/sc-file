"""
Extensions for MCSA file format with custom struct-based I/O methods.
"""

from typing import TypeAlias

import numpy as np

from scfile.consts import Factor, McsaModel, McsaSize
from scfile.core.io.streams import StructFileIO
from scfile.enums import StructFormat as F
from scfile.structures.mesh import BonesMapping
from scfile.structures.vectors import LinksIds, LinksWeights

from .exceptions import McsaCountsLimit


Links: TypeAlias = tuple[LinksIds, LinksWeights]


class McsaFileIO(StructFileIO):
    def readcount(self, type: str) -> int:
        count = self.readb(F.U32)

        if count > McsaModel.GEOMETRY_LIMIT:
            raise McsaCountsLimit(self.path, type, count)

        return count

    def readarray(self, fmt: str, dtype: str):
        return np.array(self.unpack(fmt), dtype=np.dtype(dtype))

    def readvertex(self, dtype: F, fmt: str, factor: float, size: int, count: int, scale: float = 1.0):
        # Read array
        data = self.readarray(fmt=f"{count * size}{fmt}", dtype=fmt)

        # TODO: astype before rescale?
        # Scale values to floats
        data = data * scale / factor

        return data.astype(dtype).reshape(-1, size)

    def readpolygons(self, count: int):
        size = McsaSize.POLYGONS

        # Validate that indexes fits into U16 range. Otherwise use U32.
        indexes = count * size
        fmt = F.U16 if indexes <= Factor.U16 else F.U32

        # Read array
        data = self.readarray(fmt=f"{count * size}{fmt}", dtype=fmt)

        return data.astype(F.U32).reshape(-1, size)

    def readbone(self):
        size = McsaSize.BONES

        # Read array
        data = self.readarray(fmt=f"{size}{F.F32}", dtype=F.F32)

        # Reshape to bone[position[3], rotation[3]]
        return data.astype(F.F32).reshape(2, 3)

    def readclip(self, times_count: int, bones_count: int):
        size = McsaSize.FRAMES

        # Read array
        data = self.readarray(fmt=f"{times_count * bones_count * size}{F.I16}", dtype=F.I16)

        # Scale values to floats
        data = data.astype(F.F32) / (Factor.I16)

        # Reshape to clip[frames[bones[transforms[4]]]]
        data = data.reshape(times_count, bones_count, size)

        return data

    def readpackedlinks(self, count: int, bones: BonesMapping) -> Links:
        size = McsaSize.LINKS

        # Read array
        data = self.readarray(fmt=f"{count * size}{F.U8}", dtype=F.U8)

        # Reshape to vertex[ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Unpack values
        ids, weights = padded(data[:, 0, :]), padded(data[:, 1, :])

        return links(ids.flatten(), weights.flatten(), bones)

    def readplainlinks(self, count: int, bones: BonesMapping) -> Links:
        size = McsaSize.LINKS

        # Read arrays
        ids = self.readarray(fmt=f"{count * size}{F.U8}", dtype=F.U8)
        weights = self.readarray(fmt=f"{count * size}{F.U8}", dtype=F.U8)

        return links(ids, weights, bones)


def padded(arr: np.ndarray) -> np.ndarray:
    width = ((0, 0), (0, max(0, 4 - arr.shape[-1])))
    return np.pad(arr, width, mode="constant")


def apply_bones_mapping(ids: np.ndarray, bones: BonesMapping) -> LinksIds:
    max_id = max(bones.keys())
    lookup = np.zeros(max_id + 1, dtype=F.U8)

    for k, v in bones.items():
        lookup[k] = v

    mask = np.clip(ids, 0, max_id)
    return lookup[mask]


def normalize(weights: np.ndarray) -> LinksWeights:
    reshaped = weights.reshape(-1, 4)
    normalized = reshaped / reshaped.sum(axis=1, keepdims=True)
    return normalized.reshape(-1)


def links(ids: np.ndarray, weights: np.ndarray, bones: BonesMapping) -> Links:
    # Convert local bone ids to skeleton bone ids
    ids = apply_bones_mapping(ids, bones)

    # Clean empty ids
    ids[weights == 0.0] = 0

    # Scale, Round, Normalize
    weights = weights.astype(F.F32) / Factor.U8

    # TODO: idk necessary or not
    # weights = weights.round(McsaModel.DECIMALS)
    # weights = normalize(weights)

    return (ids.astype(F.U8).reshape(-1, 4), weights.astype(F.F32).reshape(-1, 4))
