from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag
from scfile.utils.model.data import Polygon
from scfile.utils.model.mesh import ModelMesh


class ObjSerializer(FileSerializer[ModelData]):
    @property
    def model(self):
        return self.data.model

    @property
    def flags(self):
        return self.data.flags

    def serialize(self):
        self.add_meshes()

    def add_meshes(self):
        for mesh in self.model.meshes:
            self.b.writeutf8(f"o {mesh.name}\n")
            self.b.writeutf8(f"usemtl {mesh.material}\n")

            self.add_geometric_vertices(mesh)

            if self.flags[Flag.TEXTURE]:
                self.add_texture_coordinates(mesh)

            if self.flags[Flag.NORMALS]:
                self.add_vertex_normals(mesh)

            self.b.writeutf8(f"g {mesh.name}\n")
            self.add_polygonal_faces(mesh)

    def add_geometric_vertices(self, mesh: ModelMesh):
        self._write_vertex_data([f"v {v.position.x} {v.position.y} {v.position.z}" for v in mesh.vertices])

    def add_texture_coordinates(self, mesh: ModelMesh):
        self._write_vertex_data([f"vt {v.texture.u} {1.0 - v.texture.v}" for v in mesh.vertices])

    def add_vertex_normals(self, mesh: ModelMesh):
        self._write_vertex_data([f"vn {v.normals.x} {v.normals.y} {v.normals.z}" for v in mesh.vertices])

    def add_polygonal_faces(self, mesh: ModelMesh):
        self._write_vertex_data([f"f {self._polygon_to_faces(p)}" for p in mesh.global_polygons])

    def _write_vertex_data(self, data: list[str]):
        self.b.writeutf8("\n".join(data))
        self.b.write(b"\n\n")

    def _polygon_to_faces(self, polygon: Polygon):
        a, b, c = polygon.a, polygon.b, polygon.c

        # TODO: find fastest switch case (for example bits or str mask)
        if self.flags[Flag.TEXTURE] and self.flags[Flag.NORMALS]:
            return f"{a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}"

        if self.flags[Flag.TEXTURE]:
            return f"{a}/{a} {b}/{b} {c}/{c}"

        if self.flags[Flag.NORMALS]:
            return f"{a}//{a} {b}//{b} {c}//{c}"

        return f"{a} {b} {c}"
