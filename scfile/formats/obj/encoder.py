from typing import NamedTuple

from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.formats.mcsa.flags import Flag
from scfile.structures.mesh import ModelMesh


class TemplateFlags(NamedTuple):
    texture: bool
    normals: bool


FACES_TEMPLATE: dict[TemplateFlags, str] = {
    TemplateFlags(True, True): "f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}",
    TemplateFlags(True, False): "f {a}/{a} {b}/{b} {c}/{c}",
    TemplateFlags(False, True): "f {a}//{a} {b}//{b} {c}//{c}",
    TemplateFlags(False, False): "f {a} {b} {c}",
}


class ObjEncoder(FileEncoder[ModelContent, ModelOptions]):
    format = FileFormat.OBJ

    _options = ModelOptions

    def prepare(self):
        self.data.scene.flip_v_textures()
        self.data.scene.ensure_unique_names()
        self.data.scene.convert_polygons_to_faces(start_index=1)

    def serialize(self):
        self.add_meshes()

    def add_meshes(self):
        for mesh in self.data.meshes:
            self.writeutf8(f"o {mesh.name}\n")
            self.writeutf8(f"usemtl {mesh.material}\n")

            self.add_geometric_vertices(mesh)

            if self.data.flags[Flag.TEXTURE]:
                self.add_texture_coordinates(mesh)

            if self.data.flags[Flag.NORMALS]:
                self.add_vertex_normals(mesh)

            self.writeutf8(f"g {mesh.name}\n")
            self.add_polygonal_faces(mesh)

    def add_geometric_vertices(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"v {v.position.x} {v.position.y} {v.position.z}" for v in mesh.vertices]))
        self.write(b"\n\n")

    def add_texture_coordinates(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"vt {v.texture.u} {v.texture.v}" for v in mesh.vertices]))
        self.write(b"\n\n")

    def add_vertex_normals(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"vn {v.normals.x} {v.normals.y} {v.normals.z}" for v in mesh.vertices]))
        self.write(b"\n\n")

    def add_polygonal_faces(self, mesh: ModelMesh):
        flags = TemplateFlags(self.data.flags[Flag.TEXTURE], self.data.flags[Flag.NORMALS])
        template = FACES_TEMPLATE[flags]

        self.writeutf8("\n".join([template.format(a=face.a, b=face.b, c=face.c) for face in mesh.faces]))
        self.write(b"\n\n")
