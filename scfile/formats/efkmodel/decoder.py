from typing import override

from scfile.core import Decoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.io.models import ModelReader
from scfile.structures import models as S


class EfkmodelDecoder(Decoder[ModelContent, ModelReader]):
    format = FileFormat.EFKMODEL
    order = ByteOrder.LITTLE

    content_type = ModelContent
    io_factory = ModelReader

    @override
    def _parse(self):
        self.data.meta.version = self.io.value(F.U32)

        self._ctx["SCALE"] = self.io.value(F.F32)
        meshes = self.io.count(F.I32, Limit.MESHES)
        self.data.meta.counts.meshes = meshes
        self.io.skip(4)

        for _ in range(meshes):
            mesh = S.ModelMesh()
            counts = S.MeshCounts()

            # Read vertex data
            counts.vertices = self.io.count(F.U32, Limit.VERTICES)
            data = self.io.array(F.F32, counts.vertices * 15).reshape((counts.vertices, 15))
            mesh.vertices = data[:, 0:3]
            mesh.normals = data[:, 3:6]
            mesh.uv1 = data[:, 12:14]

            # Read polygons data
            counts.polygons = self.io.count(F.U32, Limit.POLYGONS)
            mesh.polygons = self.io.array(F.I32, counts.polygons * 3).astype(F.I32).reshape(-1, 3)

            self.data.scene.meshes.append(mesh)
