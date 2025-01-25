from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.formats.mcsa.flags import Flag
from scfile.geometry.mesh import ModelMesh
from scfile.geometry.scene import ModelFlags
from scfile.geometry.vectors import Polygon


def polygon_to_faces(polygon: Polygon, flags: ModelFlags):
    a, b, c = polygon.a, polygon.b, polygon.c

    if flags[Flag.TEXTURE] and flags[Flag.NORMALS]:
        return f"{a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}"

    if flags[Flag.TEXTURE]:
        return f"{a}/{a} {b}/{b} {c}/{c}"

    if flags[Flag.NORMALS]:
        return f"{a}//{a} {b}//{b} {c}//{c}"

    return f"{a} {b} {c}"


class ObjEncoder(FileEncoder[ModelContent, ModelOptions]):
    format = FileFormat.OBJ

    _options = ModelOptions

    def prepare(self):
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
        self.writeutf8("\n".join([f"vt {v.texture.u} {1.0 - v.texture.v}" for v in mesh.vertices]))
        self.write(b"\n\n")

    def add_vertex_normals(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"vn {v.normals.x} {v.normals.y} {v.normals.z}" for v in mesh.vertices]))
        self.write(b"\n\n")

    def add_polygonal_faces(self, mesh: ModelMesh):
        self.writeutf8("\n".join([f"f {polygon_to_faces(polygon, self.data.flags)}" for polygon in mesh.faces]))
        self.write(b"\n\n")
