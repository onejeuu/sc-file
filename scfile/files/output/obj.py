from dataclasses import dataclass
from typing import Any, Dict, Generator

from scfile.utils.model import Model, Vertex

from .base import BaseOutputFile, OutputData


@dataclass
class ObjOutputData(OutputData):
    model: Model


class ObjFile(BaseOutputFile[ObjOutputData]):
    def write(self) -> None:
        #self._add_material()
        self._add_geometric_vertices()
        self._add_texture_coordinates()
        #self._add_vertex_normals()
        self._ensure_unique_names()
        self._add_polygonal_faces()

    def _add_material(self) -> None:
        self._write_str(f"mtllib {self.filename}.mtl", "\n\n")

    def _add_geometric_vertices(self) -> None:
        for vertex in self._vertices():
            pos = vertex.position
            self._write_str(f"v {pos.x} {pos.y} {pos.z}\n")
        self._write_str("\n")

    def _add_texture_coordinates(self) -> None:
        for vertex in self._vertices():
            tex = vertex.texture
            self._write_str(f"vt {tex.u} {1.0 - tex.v}\n")
        self._write_str("\n")

    def _add_vertex_normals(self) -> None:
        for vertex in self._vertices():
            norm = vertex.normals
            self._write_str(f"vn {norm.i} {norm.j}\n")

        self._write_str("\n")

    def _ensure_unique_names(self):
        names: Dict[bytes, int] = {}

        # Checking names for uniqueness
        for index, mesh in enumerate(self.data.model.meshes):
            name = mesh.name

            names.setdefault(name, 0)
            names[name] += 1
            count = names[name]

            # If name already taken set name with count
            if count > 1:
                mesh.name = name + b"_" + str(count).encode()

            # If name is empty set "noname" with index
            if len(name) < 1:
                mesh.name = b"noname_" + str(index+1).encode()

    def _add_polygonal_faces(self) -> None:
        offset = 0

        for mesh in self.data.model.meshes:
            name = mesh.name.decode()
            self._write_str(f"o {name}\ng {name}\n\n")

            for polygon in mesh.polygons:
                v1 = offset + polygon.v1
                v2 = offset + polygon.v2
                v3 = offset + polygon.v3
                self._write_str(f"f {v1}/{v1} {v2}/{v2} {v3}/{v3}\n")
            self._write_str("\n")

            # Vertex id in mcsa are local to each mesh.
            offset += len(mesh.vertices)

    def _vertices(self) -> Generator[Vertex, Any, Any]:
        for mesh in self.data.model.meshes:
            for vertex in mesh.vertices:
                yield vertex
