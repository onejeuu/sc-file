"""
Model-specific structured I/O.
"""

import numpy as np

from scfile.consts import Factor
from scfile.enums import F
from scfile.structures import models as S
from scfile.structures.models import ModelUnits as Units

from .base import StructReader


class ModelReader(StructReader):
    def vertex(
        self,
        fmt: str,
        factor: float,
        units: int,
        count: int,
        scale: float = 1.0,
    ) -> np.ndarray:
        # Read array
        data = self.array(fmt, count * units)

        # Scale values to floats
        data = data.astype(F.F32) * np.float32(scale / factor)

        # Reshape to vertex[attribute[units]]
        # attribute = position[3] / normal[3] / uv[2]
        return data.reshape(-1, units)

    def normals(
        self,
        count: int,
    ) -> S.Vector3D:
        normals = self.vertex(
            fmt=F.I8,
            factor=Factor.I8,
            units=Units.NORMALS,
            count=count,
        )[:, :3]
        norm = np.linalg.norm(normals, axis=1, keepdims=True)
        return np.divide(normals, norm, out=np.zeros_like(normals), where=norm != 0)

    def tangents(
        self,
        count: int,
    ) -> S.Vector4D:
        tangents = self.vertex(
            fmt=F.I8,
            factor=Factor.I8,
            units=Units.TANGENTS,
            count=count,
        )

        xyz = tangents[:, :3]
        norm = np.linalg.norm(xyz, axis=1, keepdims=True)
        tangents[:, :3] = np.divide(xyz, norm, out=np.zeros_like(xyz), where=norm != 0)

        w = tangents[:, 3]
        tangents[:, 3] = np.where(w >= 0, 1.0, -1.0)

        return tangents

    def blend_shapes(
        self,
        count: int,
        vertices: int,
        blend_vertex_map: S.BlendVertexMap,
    ) -> S.Vector3D:
        # Read shape[base vertex][xyz + padding]
        data = self.array(F.U8, count * vertices * 4).reshape(count, vertices, 4)

        # Center and normalize position deltas
        deltas = data[:, :, :3].astype(F.F32)
        deltas -= Factor.I8
        deltas /= Factor.U8

        # Expand base vertices to mesh vertices
        return deltas[:, blend_vertex_map]

    def polygons(
        self,
        count: int,
        quads: bool = False,
    ) -> S.Polygons:
        units = Units.QUADS if quads else Units.TRIANGLES

        # ? Validate that indexes fits into U16 range, otherwise use U32.
        indexes = count * units
        fmt = F.U16 if indexes <= Factor.U16 else F.U32

        # Read array
        data = self.array(fmt, count * units)

        # Reshape to face[indices[3]]
        if quads:
            data = data.reshape(-1, Units.QUADS)
            tri1 = data[:, [0, 1, 2]]
            tri2 = data[:, [0, 2, 3]]
            return np.concatenate([tri1, tri2]).astype(F.U32)

        # Reshape to face[indices[3]]
        return data.astype(F.U32).reshape(-1, units)

    def bone(self) -> S.Vector3D:
        units = Units.BONES

        # Read array
        data = self.array(F.F32, units)

        # Reshape to bone[head[3], tail[3]]
        return data.astype(F.F32).reshape(2, 3)

    def clip(
        self,
        times_count: int,
        bones_count: int,
        channels_count: int,
        position_scale: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        units = Units.FRAMES
        frame_size = bones_count * units + channels_count

        # Read bone transforms and morph weights
        data = self.array(F.U16, times_count * frame_size)
        data = data.reshape(times_count, frame_size)
        transforms = data[:, : bones_count * units].view(f"{self.order}{F.I16}")
        morph_weights = data[:, bones_count * units :].astype(F.F32)
        morph_weights *= np.float32(1.0 / Factor.I16)

        # Reshape to clip[frames][bones][transforms[7]]
        # transforms = [rotation[4], translation[3]]
        data = transforms.astype(F.F32).reshape(times_count, bones_count, units)
        rotations = data[:, :, :4] * np.float32(1.0 / Factor.I16)
        translations = data[:, :, 4:7] * np.float32(position_scale / Factor.I16)

        return rotations, translations, morph_weights

    def packed_links(
        self,
        count: int,
        bones: S.BonesMapping,
    ) -> S.Links:
        units = Units.LINKS

        # Read array
        data = self.array(F.U8, count * units)

        # Reshape to vertex[skin[2][2]]
        # skin = [bone_ids[2], weights[2]]
        data = data.reshape(-1, 2, 2)

        # Unpack and pad values
        ids, weights = _padded(data[:, 0, :]), _padded(data[:, 1, :])

        return _links(ids.flatten(), weights.flatten(), bones)

    def plain_links(
        self,
        count: int,
        bones: S.BonesMapping,
    ) -> S.Links:
        units = Units.LINKS

        # Read arrays: bone_ids[vertex][units], weights[vertex][units]
        ids = self.array(F.U8, count * units)
        weights = self.array(F.U8, count * units)

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
