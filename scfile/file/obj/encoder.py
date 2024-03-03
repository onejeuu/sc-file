from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder
from scfile.utils.model import Mesh


class ObjEncoder(FileEncoder[ModelData]):
    def serialize(self):
        # TODO: Improve old implementation (maybe)

        self.offset = 0
        self._ensure_unique_names()

        self.references_count = 1 + int(self.flags.texture) + int(self.flags.normals)

        for mesh in self.meshes:
            self._add_geometric_vertices(mesh)

            if self.flags.texture:
                self._add_texture_coordinates(mesh)

            if self.flags.normals:
                self._add_vertex_normals(mesh)

            self.b.writeascii(f"g {mesh.name}\n")
            self._add_polygonal_faces(mesh)

    @property
    def meshes(self):
        return self.data.model.meshes

    @property
    def flags(self):
        return self.data.model.flags

    def _add_geometric_vertices(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [f"v {v.position.x} {v.position.y} {v.position.z}" for v in mesh.vertices]
        )

    def _add_texture_coordinates(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [f"vt {v.texture.u} {1.0 - v.texture.v}" for v in mesh.vertices]
        )

    def _add_vertex_normals(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [f"vn {v.normals.x} {v.normals.y} {v.normals.z}" for v in mesh.vertices]
        )

    def _add_polygonal_faces(self, mesh: Mesh) -> None:
        self._write_vertex_data(
            [
                f"f {self._vertex_id(p.v1)} {self._vertex_id(p.v2)} {self._vertex_id(p.v3)}"
                for p in mesh.polygons
            ]
        )

        # TODO: Move this to parsing with backwards compatibility
        # Vertex id in mcsa are local to each mesh.
        self.offset += mesh.offset

    def _vertex_id(self, v: int) -> str:
        # TODO: Reduce number of calls
        # TODO: Fix bad implementation via references_count (v/vt/vn)
        return "/".join([str(v + self.offset)] * self.references_count)

    def _write_vertex_data(self, data: list[str]) -> None:
        self.b.writeascii("\n".join(data))
        self.b.write(b"\n\n")

    def _ensure_unique_names(self):
        seen_names: set[str] = set()

        for mesh in self.meshes:
            name = mesh.name

            if not name:
                name = "noname"

            base_name, count = name, 2
            unique_name = f"{base_name}"

            while unique_name in seen_names:
                unique_name = f"{base_name}_{count}"
                count += 1

            mesh.name = unique_name
            seen_names.add(unique_name)
