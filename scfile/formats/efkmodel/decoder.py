from scfile import formats
from scfile.consts import ModelDefaults
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.decoder import MeshCounts
from scfile.formats.mcsa.exceptions import McsaCountsLimit
from scfile.formats.mcsa.io import McsaFileIO
from scfile.structures import models as S


class EfkmodelDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.EFKMODEL
    order = ByteOrder.LITTLE

    _content = ModelContent

    def to_obj(self):
        return self.convert_to(formats.obj.ObjEncoder)

    def to_glb(self):
        return self.convert_to(formats.glb.GlbEncoder)

    def to_fbx(self):
        return self.convert_to(formats.fbx.FbxEncoder)

    def to_dae(self):
        return self.convert_to(formats.dae.DaeEncoder)

    def to_ms3d(self):
        return self.convert_to(formats.ms3d.Ms3dEncoder)

    def parse(self):
        self.data.version = self._readb(F.U32)

        self.ctx["SCALE"] = self._readb(F.F32)
        self.ctx["COUNT_MESHES"] = self._readb(F.I32)
        self.ctx["COUNT_CLIPS"] = self._readb(F.I32)

        for _ in range(self.ctx["COUNT_MESHES"]):
            mesh = S.ModelMesh()
            counts = MeshCounts()

            # Read vertex data
            counts.vertices = self._parse_count("vertices")
            data = self._readarray(F.F32, counts.vertices * 15).reshape((counts.vertices, 15))
            mesh.vertices = data[:, 0:3]
            mesh.normals = data[:, 3:6]
            mesh.uv1 = data[:, 12:14]

            # Read polygons data
            counts.polygons = self._parse_count("polygons")
            mesh.polygons = self._readarray(F.I32, counts.polygons * 3).astype(F.I32).reshape(-1, 3)

            self.data.scene.meshes.append(mesh)

    def _parse_count(self, type: str) -> int:
        count = self._readb(F.U32)

        # ? Prevent memory overflow
        if count > ModelDefaults.GEOMETRY_LIMIT:
            raise McsaCountsLimit(self.location, type, count)

        return count
