from scfile.file.encoder import FileEncoder
from scfile.file.data import ModelData
from scfile.utils.model import Mesh


class ObjEncoder(FileEncoder[ModelData]):
    def serialize(self):
        # TODO: Temporary code, will be improved

        self.offset = 0
        self._ensure_unique_names()

        for mesh in self.meshes:
            self._add_geometric_vertices(mesh)

            if self.data.texture:
                self._add_texture_coordinates(mesh)

            if self.data.normals:
                self._add_vertex_normals(mesh)

            self.b.writes(f"g {mesh.name}\n")
            self._add_polygonal_faces(mesh)

    @property
    def meshes(self):
        return self.data.model.meshes

    @property
    def references_count(self):
        return 1 + int(self.data.texture) + int(self.data.normals)

    def _add_geometric_vertices(self, mesh: Mesh) -> None:
        for v in mesh.vertices:
            self.b.writes(f"v {v.position.x} {v.position.y} {v.position.z}\n")
        self.b.writes("\n")

    def _add_texture_coordinates(self, mesh: Mesh) -> None:
        for v in mesh.vertices:
            self.b.writes(f"vt {v.texture.u} {1.0 - v.texture.v}\n")
        self.b.writes("\n")

    def _add_vertex_normals(self, mesh: Mesh) -> None:
        for v in mesh.vertices:
            self.b.writes(f"vn {v.normals.x} {v.normals.y} {v.normals.z}\n")
        self.b.writes("\n")

    def _vertex_id(self, v: int):
        return "/".join([str(v)] * self.references_count)

    def _add_polygonal_faces(self, mesh: Mesh) -> None:
        for polygon in mesh.polygons:
            v1 = polygon.v1 + self.offset
            v2 = polygon.v2 + self.offset
            v3 = polygon.v3 + self.offset
            self.b.writes(f"f {self._vertex_id(v1)} {self._vertex_id(v2)} {self._vertex_id(v3)}\n")
        self.b.writes("\n")

        # TODO: Move this to parsing with backwards compatibility
        # Vertex id in mcsa are local to each mesh.
        self.offset += len(mesh.vertices)

    def _ensure_unique_names(self):
        seen_names = set()

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
