import numpy as np

from scfile.core import FileEncoder, ModelContent
from scfile.enums import FileFormat
from scfile.structures.flags import Flag
from scfile.structures.mesh import ModelMesh

from . import faces


class ObjEncoder(FileEncoder[ModelContent]):
    format = FileFormat.OBJ

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self.data.flags[Flag.UV]:
            self.data.scene.flip_v_textures()

    def serialize(self):
        self._add_meshes()

    def _add_meshes(self):
        offset = 1

        for mesh in self.data.scene.meshes:
            self._writeutf8(f"o {mesh.name}\n")
            self._writeutf8(f"usemtl {mesh.material}\n")

            self._add_geometric_vertices(mesh)

            if self.data.flags[Flag.UV]:
                self._add_texture_coordinates(mesh)

            if self.data.flags[Flag.NORMALS]:
                self._add_vertex_normals(mesh)

            self._writeutf8(f"g {mesh.name}\n")
            self._add_polygonal_faces(mesh, offset)

            offset += mesh.count.vertices

    def _vectorize(self, template: bytes, data: np.ndarray, count: int):
        return (template * count) % tuple(data.flatten().tolist())

    def _add_geometric_vertices(self, mesh: ModelMesh):
        template = b"v %.6f %.6f %.6f\n"
        self.write(self._vectorize(template, mesh.positions, mesh.count.vertices))
        self.write(b"\n")

    def _add_texture_coordinates(self, mesh: ModelMesh):
        template = b"vt %.6f %.6f\n"
        self.write(self._vectorize(template, mesh.textures, mesh.count.vertices))
        self.write(b"\n")

    def _add_vertex_normals(self, mesh: ModelMesh):
        template = b"vn %.6f %.6f %.6f\n"
        self.write(self._vectorize(template, mesh.normals, mesh.count.vertices))
        self.write(b"\n")

    def _add_polygonal_faces(self, mesh: ModelMesh, offset: int):
        flags = faces.Flags(uv=self.data.flags[Flag.UV], normals=self.data.flags[Flag.NORMALS])
        template = faces.TEMPLATE[flags]

        polygons = mesh.polygons + offset
        self._writeutf8("\n".join([template.format(a=a, b=b, c=c) for a, b, c in polygons.tolist()]))
        self.write(b"\n\n")
