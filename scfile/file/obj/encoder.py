from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder
from scfile.utils.model import Mesh


class ObjEncoder(FileEncoder[ModelData]):
    def serialize(self):
        # TODO: Improve old implementation (maybe)

        self.offset = 0
        self.model.ensure_unique_names()

        # TODO: Fix bad implementation via references_count (v/vt/vn)
        # ? As rule almost models have texture but not normals
        self.references_count = 1 + int(self.flags.texture) + int(self.flags.normals)

        for mesh in self.model.meshes:
            self._add_geometric_vertices(mesh)

            if self.flags.texture:
                self._add_texture_coordinates(mesh)

            if self.flags.normals:
                self._add_vertex_normals(mesh)

            self.b.writeascii(f"g {mesh.name}\n")
            self._add_polygonal_faces(mesh)

    @property
    def model(self):
        return self.data.model

    @property
    def flags(self):
        return self.data.model.flags

    def _add_geometric_vertices(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [f"v {v.position.x:.6f} {v.position.y:.6f} {v.position.z:.6f}" for v in mesh.vertices]
        )

    def _add_texture_coordinates(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [f"vt {v.texture.u:.6f} {1.0 - v.texture.v:.6f}" for v in mesh.vertices]
        )

    def _add_vertex_normals(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [f"vn {v.normals.x:.6f} {v.normals.y:.6f} {v.normals.z:.6f}" for v in mesh.vertices]
        )

    def _add_polygonal_faces(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [
                f"f {self._vertex_id(p.a)} {self._vertex_id(p.b)} {self._vertex_id(p.c)}"
                for p in mesh.polygons
            ]
        )

        # TODO: Move this to parsing with backwards compatibility
        # Vertex id in mcsa are local to each mesh.
        self.offset += mesh.offset

    def _vertex_id(self, v: int) -> str:
        # TODO: Reduce number of calls
        vertex_id = str(v + self.offset)
        return "/".join([vertex_id] * self.references_count)

    def _write_vertex_data(self, data: list[str]) -> None:
        self.b.writeascii("\n".join(data))
        self.b.write(b"\n\n")
