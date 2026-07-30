from scfile import formats
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.formats.mcsa.decoder import MeshCounts
from scfile.io.models import ModelReader
from scfile.structures import models as S


class EfkmodelDecoder(FileDecoder[ModelContent, ModelReader]):
    format = FileFormat.EFKMODEL
    order = ByteOrder.LITTLE

    content_type = ModelContent
    io_factory = ModelReader

    def as_obj(self):
        return self.convert_to(formats.obj.ObjEncoder)

    def as_glb(self):
        return self.convert_to(formats.glb.GlbEncoder)

    def as_fbx(self):
        return self.convert_to(formats.fbx.FbxEncoder)

    def as_dae(self):
        return self.convert_to(formats.dae.DaeEncoder)

    def as_ms3d(self):
        return self.convert_to(formats.ms3d.Ms3dEncoder)

    def _parse(self):
        self.data.version = self.io.value(F.U32)

        self.ctx["SCALE"] = self.io.value(F.F32)
        self.ctx["COUNT_MESHES"] = self.io.count(F.I32, Limit.MESHES)
        self.ctx["COUNT_UNKNOWN"] = self.io.value(F.I32)

        for _ in range(self.ctx["COUNT_MESHES"]):
            mesh = S.ModelMesh()
            counts = MeshCounts()

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
