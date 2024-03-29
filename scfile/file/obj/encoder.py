from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder
from scfile.utils.model import Mesh, Polygon


class ObjEncoder(FileEncoder[ModelData]):
    FLOAT_FORMAT = ".6f"

    def serialize(self):
        self.model = self.data.model
        self.flags = self.data.model.flags

        self.offset = 0
        self.model.ensure_unique_names()

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
        f = self.FLOAT_FORMAT
        self._write_vertex_data(
            [f"v {v.position.x:{f}} {v.position.y:{f}} {v.position.z:{f}}" for v in mesh.vertices]
        )

    def _add_texture_coordinates(self, mesh: Mesh):
        f = self.FLOAT_FORMAT
        self._write_vertex_data(
            [f"vt {v.texture.u:{f}} {1.0 - v.texture.v:{f}}" for v in mesh.vertices]
        )

    def _add_vertex_normals(self, mesh: Mesh):
        f = self.FLOAT_FORMAT
        self._write_vertex_data(
            [f"vn {v.normals.x:{f}} {v.normals.y:{f}} {v.normals.z:{f}}" for v in mesh.vertices]
        )

    def _add_polygonal_faces(self, mesh: Mesh):
        self._write_vertex_data([f"f {self._polygon_to_faces(p)}" for p in mesh.polygons])

        # Vertex id in mcsa are local to each mesh.
        self.offset += mesh.offset

    def _write_vertex_data(self, data: list[str]):
        self.b.writes("\n".join(data))
        self.b.write(b"\n\n")

    def _polygon_to_faces(self, polygon: Polygon):
        a, b, c = polygon.a + self.offset, polygon.b + self.offset, polygon.c + self.offset

        if self.flags.texture and self.flags.normals:
            return f"{a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}"

        if self.flags.texture:
            return f"{a}/{a} {b}/{b} {c}/{c}"

        if self.flags.normals:
            return f"{a}//{a} {b}//{b} {c}//{c}"

        return f"{a} {b} {c}"
