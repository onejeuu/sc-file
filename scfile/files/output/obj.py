from io import BytesIO
from typing import Any, Generator

from scfile.utils.model import Model, Vector, Vertex

from .base import BaseOutputFile


class ObjFile(BaseOutputFile):
    def __init__(
        self,
        buffer: BytesIO,
        filename: str,
        model: Model,
    ):
        super().__init__(buffer, filename)
        self.model = model

    def _create(self) -> None:
        self._add_header()
        self._add_geometric_vertices()
        self._add_texture_coordinates()
        self._add_vertex_normals()
        self._add_polygonal_faces()

    def _add_header(self) -> None:
        self._write(
            "# OBJ Model", "\n",
            "# scfile", "\n",
            "\n",
            "mtllib", " ", self.filename, ".mtl", "\n",
            "o", " ", self.filename, "\n",
            "\n"
        )

    def _add_geometric_vertices(self) -> None:
        for vertex in self._vertices():
            self._write(
                "v", " ",
                vertex.position.x, " ",
                vertex.position.y, " ",
                vertex.position.z, " ",
                "\n"
            )
        self._write("\n")

    def _add_texture_coordinates(self) -> None:
        for vertex in self._vertices():
            self._write(
                "vt", " ",
                vertex.texture.u, " ",
                1.0 - vertex.texture.v, " ",
                "\n"
            )
        self._write("\n")

    def _add_vertex_normals(self) -> None:
        for vertex in self._vertices():
            self._write(
                "vn", " ",
                vertex.normals.x, " ",
                vertex.normals.y, " ",
                vertex.normals.z, " ",
                "\n"
            )

            if self._normals_is_empty(vertex.normals):
                break

        self._write("\n")

    def _add_polygonal_faces(self) -> None:
        self._write("g", " ", self.filename, "\n")

        for index, mesh in self.model.meshes.items():
            self._write("usemtl", " ", f"{index}_{mesh.material.decode()}", "\n")

            for index, polygon in enumerate(mesh.polygons):
                self._write(
                    "f", " ",
                    polygon.vertex1, "/", polygon.vertex1, "/", 1, " ",
                    polygon.vertex2, "/", polygon.vertex2, "/", 1, " ",
                    polygon.vertex3, "/", polygon.vertex3, "/", 1,
                    "\n"
                )

    def _normals_is_empty(self, normals: Vector) -> bool:
        return all(_ == 0.0 for _ in (normals.x, normals.y, normals.z))

    def _vertices(self) -> Generator[Vertex, Any, Any]:
        for mesh in self.model.meshes.values():
            for vertex in mesh.vertices:
                yield vertex

    def _write(self, *data: Any) -> None:
        string = "".join([str(i) for i in data])
        self.buffer.write(string.encode())
