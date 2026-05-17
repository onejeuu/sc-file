"""
Extensions for MCSA file format with custom struct-based I/O methods.
"""

import numpy as np

from scfile.consts import Factor, ModelDefaults
from scfile.core.io import StructFileIO
from scfile.enums import F
from scfile.structures import models as S

from .consts import McsaUnits
from .exceptions import McsaCountsLimit


class McsaFileIO(StructFileIO):
    def _readcount(self, type: str) -> int:
        count = self._readb(F.U32)

        # ? Prevent memory overflow
        if count > ModelDefaults.GEOMETRY_LIMIT:
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

    def _readnormals(self, count: int):
        normals = self._readvertex(
            fmt=F.I8,
            factor=Factor.I8,
            units=McsaUnits.NORMALS,
            count=count,
        )[:, :3]
        norm = np.linalg.norm(normals, axis=1, keepdims=True)
        return np.divide(normals, norm, out=np.zeros_like(normals), where=norm != 0)

    def _readtangents(self, count: int):
        tangents = self._readvertex(
            fmt=F.I8,
            factor=Factor.I8,
            units=McsaUnits.TANGENTS,
            count=count,
        )

        xyz = tangents[:, :3]
        norm = np.linalg.norm(xyz, axis=1, keepdims=True)
        tangents[:, :3] = np.divide(xyz, norm, out=np.zeros_like(xyz), where=norm != 0)

        w = tangents[:, 3]
        tangents[:, 3] = np.where(w >= 0, 1.0, -1.0)

        return tangents

    def _readpolygons(self, count: int, quads: bool = False):
        units = McsaUnits.QUADS if quads else McsaUnits.TRIANGLES

        # ? Validate that indexes fits into U16 range, otherwise use U32.
        indexes = count * units
        fmt = F.U16 if indexes <= Factor.U16 else F.U32

        # Read array
        data = self._readarray(fmt, count * units)

        # Reshape to face[indices[3]]
        if quads:
            data = data.reshape(-1, McsaUnits.QUADS)
            tri1 = data[:, [0, 1, 2]]
            tri2 = data[:, [0, 2, 3]]
            return np.concatenate([tri1, tri2]).astype(F.U32)

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
        data = data.reshape(times_count, bones_count, units)
        rotations = data[:, :, :4]
        translations = data[:, :, 4:7]

        return rotations, translations

    def _readpackedlinks(self, count: int, bones: S.BonesMapping) -> S.Links:
        units = McsaUnits.LINKS

        # Read array
        data = self._readarray(F.U8, count * units)

        # Reshape to vertex[skin[2][2]]
        # skin = [bone_ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Unpack and pad values
        ids, weights = _padded(data[:, 0, :]), _padded(data[:, 1, :])

        return _links(ids.flatten(), weights.flatten(), bones)

    def _readplainlinks(self, count: int, bones: S.BonesMapping) -> S.Links:
        units = McsaUnits.LINKS

        # Read arrays: bone_ids[vertex][units], weights[vertex][units]
        ids = self._readarray(F.U8, count * units)
        weights = self._readarray(F.U8, count * units)

        return _links(ids, weights, bones)


def _padded(arr: np.ndarray) -> np.ndarray:
    width = ((0, 0), (0, max(0, 4 - arr.shape[-1])))
    return np.pad(arr, width, mode="constant")


def _apply_bones_mapping(ids: np.ndarray, bones: S.BonesMapping) -> S.LinksIds:
    max_id = max(bones.keys())
    lookup = np.zeros(max_id + 1, dtype=F.U8)

    for k, v in bones.items():
        lookup[k] = v

    mask = np.clip(ids, 0, max_id)
    return lookup[mask]


def _links(ids: np.ndarray, weights: np.ndarray, bones: S.BonesMapping) -> S.Links:
    ids = _apply_bones_mapping(ids, bones)
    ids[weights == 0.0] = 0

    weights = weights.astype(F.F32) * np.float32(1.0 / Factor.U8)

    # Normalize weights
    weights = weights.reshape(-1, 4)
    sums = weights.sum(axis=1, keepdims=True)
    weights = np.divide(weights, sums, out=np.zeros_like(weights), where=sums != 0)

    return (ids.astype(F.U8).reshape(-1, 4), weights.astype(F.F32))
