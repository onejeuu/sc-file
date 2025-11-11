from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.io import McsaFileIO
from scfile.structures.mesh import ModelMesh


class EfkmodelDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCSA
    order = ByteOrder.LITTLE

    _content = ModelContent

    def parse(self):
        self.data.version = self._readb(F.U32)

        self._readb(F.F32)  # ? Scale
        self.data.scene.count.meshes = self._readb(F.I32)
        self._readb(F.I32)  # ? Animation count

        for _ in range(self.data.scene.count.meshes):
            mesh = ModelMesh()

            # Read vertex data
            mesh.count.vertices = self._readcount("vertices")
            data = self._readarray(F.F32, mesh.count.vertices * 15).reshape((mesh.count.vertices, 15))
            mesh.positions = data[:, 0:3]
            mesh.normals = data[:, 3:6]
            mesh.textures = data[:, 12:14]

            # Read polygons data
            mesh.count.polygons = self._readcount("polygons")
            mesh.polygons = self._readarray(F.U32, mesh.count.polygons * 3).astype(F.U32).reshape(-1, 3)

            self.data.scene.meshes.append(mesh)
