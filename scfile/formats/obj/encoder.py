from typing import NamedTuple

from scfile.core import FileEncoder
from scfile.core.context import ModelContent
from scfile.enums import FileFormat
from scfile.formats.mcsa.flags import Flag
from scfile.structures.mesh import ModelMesh


class TemplateFlags(NamedTuple):
    uv: bool
    normals: bool


FACES_TEMPLATE: dict[TemplateFlags, str] = {
    TemplateFlags(True, True): "f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}",
    TemplateFlags(True, False): "f {a}/{a} {b}/{b} {c}/{c}",
    TemplateFlags(False, True): "f {a}//{a} {b}//{b} {c}//{c}",
    TemplateFlags(False, False): "f {a} {b} {c}",
}


class ObjEncoder(FileEncoder[ModelContent]):
    format = FileFormat.OBJ

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self.data.flags[Flag.UV]:
            self.data.scene.flip_v_textures()

    def serialize(self):
        self.add_meshes()

    def add_meshes(self):
        offset = 1
        for mesh in self.data.scene.meshes:
            self.writeutf8(f"o {mesh.name}\n")
            self.writeutf8(f"usemtl {mesh.material}\n")

            self.add_geometric_vertices(mesh)

            if self.data.flags[Flag.UV]:
                self.add_texture_coordinates(mesh)

            if self.data.flags[Flag.NORMALS]:
                self.add_vertex_normals(mesh)

            self.writeutf8(f"g {mesh.name}\n")
            self.add_polygonal_faces(mesh, offset)
            offset += mesh.count.vertices

    def add_geometric_vertices(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"v {x:.6} {y:.6f} {z:.6f}" for x, y, z in mesh.positions]))
        self.write(b"\n\n")

    def add_texture_coordinates(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"vt {u:.6f} {v:.6f}" for u, v in mesh.textures]))
        self.write(b"\n\n")

    def add_vertex_normals(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"vn {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh.normals]))
        self.write(b"\n\n")

    def add_polygonal_faces(self, mesh: ModelMesh, offset: int):
        flags = TemplateFlags(self.data.flags[Flag.UV], self.data.flags[Flag.NORMALS])
        template = FACES_TEMPLATE[flags]

        polygons = mesh.polygons + offset
        self.writeutf8("\n".join([template.format(a=a, b=b, c=c) for a, b, c in polygons]))
        self.write(b"\n\n")
