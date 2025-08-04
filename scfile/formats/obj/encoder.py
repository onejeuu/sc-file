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

    def _add_geometric_vertices(self, mesh: ModelMesh):
        self._writeutf8("\n".join([f"v {x:.6} {y:.6f} {z:.6f}" for x, y, z in mesh.positions]))
        self.write(b"\n\n")

    def _add_texture_coordinates(self, mesh: ModelMesh):
        self._writeutf8("\n".join([f"vt {u:.6f} {v:.6f}" for u, v in mesh.textures]))
        self.write(b"\n\n")

    def _add_vertex_normals(self, mesh: ModelMesh):
        self._writeutf8("\n".join([f"vn {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh.normals]))
        self.write(b"\n\n")

    def _add_polygonal_faces(self, mesh: ModelMesh, offset: int):
        flags = faces.Flags(uv=self.data.flags[Flag.UV], normals=self.data.flags[Flag.NORMALS])
        template = faces.TEMPLATE[flags]

        polygons = mesh.polygons + offset
        self._writeutf8("\n".join([template.format(a=a, b=b, c=c) for a, b, c in polygons]))
        self.write(b"\n\n")
