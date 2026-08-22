from typing import override

import numpy as np

from scfile import exceptions
from scfile.core import ModelDecoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.io.models import ModelReader
from scfile.structures import models as S


_VERTEX = np.dtype(
    [
        ("position", "<f4", 3),
        ("normal", "<f4", 3),
        ("binormal", "<f4", 3),
        ("tangent", "<f4", 3),
        ("uv", "<f4", 2),
        ("color", "u1", 4),
    ]
)


class EfkmodelDecoder(ModelDecoder[ModelReader]):
    format = FileFormat.EFKMODEL
    order = ByteOrder.LITTLE

    io_factory = ModelReader
    features = (
        S.Feature.UV,
        S.Feature.UV2,
        S.Feature.NORMALS,
        S.Feature.TANGENTS,
        S.Feature.COLORS,
    )

    @override
    def _parse(self):
        self.data.meta.version = self.io.value(F.U32)
        if self.data.meta.version != 5:
            raise exceptions.ModelVersionError(self.data.meta.version, location=self.io.location)

        self.io.value(F.F32)
        self.io.value(F.I32)
        frames = self.io.count(F.I32, Limit.MESHES)
        self.data.meta.counts.meshes = frames

        mesh = S.ModelMesh()

        vertices = self.io.count(F.I32, Limit.VERTICES)
        data = np.frombuffer(self.io.read_exact(vertices * _VERTEX.itemsize), dtype=_VERTEX)
        mesh.vertices = data["position"].copy()
        mesh.normals = data["normal"].copy()
        mesh.uv1 = data["uv"].copy()
        mesh.uv2 = mesh.uv1.copy()
        mesh.colors = data["color"].copy()

        tangent = data["tangent"]
        bitangent = data["binormal"]
        handedness = np.einsum("ij,ij->i", np.cross(mesh.normals, tangent), bitangent)
        mesh.tangents = np.column_stack((tangent, np.where(handedness < 0.0, -1.0, 1.0))).astype(F.F32)

        polygons = self.io.count(F.I32, Limit.POLYGONS)
        indices = self.io.array(F.I32, polygons * 3)
        if np.any(indices < 0) or np.any(indices >= vertices):
            raise exceptions.BinaryStructureError(location=self.io.location, offset=self.io.tell())

        mesh.polygons = indices.astype(F.U32).reshape(-1, 3)

        self.data.scene.meshes.append(mesh)
