"""
Extensions for MCSA file format with custom struct-based I/O methods.
"""

from typing import TypeAlias

import numpy as np

from scfile.consts import Factor, McsaModel, McsaUnits
from scfile.core.io import StructFileIO
from scfile.enums import F
from scfile.structures.mesh import BonesMapping
from scfile.structures.vectors import LinksIds, LinksWeights

from .exceptions import McsaCountsLimit


Links: TypeAlias = tuple[LinksIds, LinksWeights]


class McsaFileIO(StructFileIO):
    def _readcount(self, type: str) -> int:
        count = self._readb(F.U32)

        # ? Prevent memory overflow
        if count > McsaModel.GEOMETRY_LIMIT:
            raise McsaCountsLimit(self.path, type, count)

        return count

    def _readvertex(self, fmt: str, factor: float, units: int, count: int, scale: float = 1.0):
        # Read array
        data = self._readarray(fmt, count * units)

        # Scale values to floats
        data = data.astype(F.F32) * np.float32(scale / factor)

        # Reshape to vertex[attribute[units]]
        # attribute = position[3] / normal[3] / uv[2]
        return data.reshape(-1, units)

    def _readpolygons(self, count: int):
        units = McsaUnits.POLYGONS

        # ? Validate that indexes fits into U16 range, otherwise use U32.
        indexes = count * units
        fmt = F.U16 if indexes <= Factor.U16 else F.U32

        # Read array
        data = self._readarray(fmt, count * units)

        # Reshape to face[indices[3]]
        return data.astype(F.U32).reshape(-1, units)

    def _readbone(self):
        units = McsaUnits.BONES

        # Read array
        data = self._readarray(F.F32, units)

        # Reshape to bone[position[3], rotation[3]]
        return data.astype(F.F32).reshape(2, 3)

    def _readclip(self, times_count: int, bones_count: int):
        units = McsaUnits.FRAMES

        # Read array
        data = self._readarray(F.I16, times_count * bones_count * units)

        # Scale values to floats
        data = data.astype(F.F32) * np.float32(1.0 / Factor.I16)

        # Reshape to clip[frames][bones][transforms[7]]
        # transforms = [rotation[4], translation[3]]
        return data.reshape(times_count, bones_count, units)

    def _readpackedlinks(self, count: int, bones: BonesMapping) -> Links:
        units = McsaUnits.LINKS

        # Read array
        data = self._readarray(F.U8, count * units)

        # Reshape to vertex[skin[2][2]]
        # skin = [bone_ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Unpack and pad values
        ids, weights = _padded(data[:, 0, :]), _padded(data[:, 1, :])

        return _links(ids.flatten(), weights.flatten(), bones)

    def _readplainlinks(self, count: int, bones: BonesMapping) -> Links:
        units = McsaUnits.LINKS

        # Read arrays: bone_ids[vertex][units], weights[vertex][units]
        ids = self._readarray(F.U8, count * units)
        weights = self._readarray(F.U8, count * units)

        return _links(ids, weights, bones)


def _padded(arr: np.ndarray) -> np.ndarray:
    width = ((0, 0), (0, max(0, 4 - arr.shape[-1])))
    return np.pad(arr, width, mode="constant")


def _apply_bones_mapping(ids: np.ndarray, bones: BonesMapping) -> LinksIds:
    max_id = max(bones.keys())
    lookup = np.zeros(max_id + 1, dtype=F.U8)

    for k, v in bones.items():
        lookup[k] = v

    mask = np.clip(ids, 0, max_id)
    return lookup[mask]


def _links(ids: np.ndarray, weights: np.ndarray, bones: BonesMapping) -> Links:
    # Convert local bone ids to skeleton bone ids
    ids = _apply_bones_mapping(ids, bones)

    # Clean empty ids
    ids[weights == 0.0] = 0

    # Scale, Round, Normalize
    weights = weights.astype(F.F32) * np.float32(1.0 / Factor.U8)

    # Reshape to vertex[bone_ids[units]], vertex[weights[units]]
    return (ids.astype(F.U8).reshape(-1, 4), weights.astype(F.F32).reshape(-1, 4))
