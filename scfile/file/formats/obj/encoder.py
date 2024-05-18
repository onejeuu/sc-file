from scfile.file.base import FileEncoder
from scfile.file.data import ModelData
from scfile.utils.model import Mesh, Polygon


class ObjEncoder(FileEncoder[ModelData]):
    def serialize(self):
        self.model = self.data.model
        self.flags = self.data.model.flags

        self.model.ensure_unique_names()
        self.model.convert_polygons_to_global(start=1)

        for mesh in self.model.meshes:
            self.b.writes(f"o {mesh.name}\n")

            self._add_geometric_vertices(mesh)

            if self.flags.texture:
                self._add_texture_coordinates(mesh)

            if self.flags.normals:
                self._add_vertex_normals(mesh)

            self.b.writes(f"g {mesh.name}\n")
            self._add_polygonal_faces(mesh)

    def _add_geometric_vertices(self, mesh: Mesh):
        self._write_vertex_data(
            [f"v {v.position.x} {v.position.y} {v.position.z}" for v in mesh.vertices]
        )

    def _add_texture_coordinates(self, mesh: Mesh):
        self._write_vertex_data([f"vt {v.texture.u} {1.0 - v.texture.v}" for v in mesh.vertices])

    def _add_vertex_normals(self, mesh: Mesh):
        self._write_vertex_data(
            [f"vn {v.normals.x} {v.normals.y} {v.normals.z}" for v in mesh.vertices]
        )

    def _add_polygonal_faces(self, mesh: Mesh):
        self._write_vertex_data([f"f {self._polygon_to_faces(p)}" for p in mesh.global_polygons])

    def _write_vertex_data(self, data: list[str]):
        self.b.writes("\n".join(data))
        self.b.write(b"\n\n")

    def _polygon_to_faces(self, polygon: Polygon):
        a, b, c = polygon.a, polygon.b, polygon.c

        if self.flags.texture and self.flags.normals:
            return f"{a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}"

        if self.flags.texture:
            return f"{a}/{a} {b}/{b} {c}/{c}"

        if self.flags.normals:
            return f"{a}//{a} {b}//{b} {c}//{c}"

        return f"{a} {b} {c}"
