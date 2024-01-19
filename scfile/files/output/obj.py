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
        self._add_texture_vertices()
        self._add_vertex_normals()
        self._ensure_unique_names()
        self._add_polygonal_faces()

    def _add_material(self) -> None:
        self._write_str(f"mtllib {self.filename}.mtl", "\n\n")

    def _add_geometric_vertices(self) -> None:
        for vertex in self._vertices():
            pos = vertex.position
            self._write_str(f"v {pos.x} {pos.y} {pos.z}\n")
        self._write_str("\n")

    def _add_texture_vertices(self) -> None:
        for vertex in self._vertices():
            tex = vertex.texture
            self._write_str(f"vt {tex.u} {1.0 - tex.v}\n")
        self._write_str("\n")

    def _add_vertex_normals(self) -> None:
        for vertex in self._vertices():
            nrm = vertex.normals
            self._write_str(f"vn {nrm.i} {nrm.j} {nrm.k}\n")

        self._write_str("\n")

    def _add_polygonal_faces(self) -> None:
        offset = 0

        for mesh in self.data.model.meshes:
            self._write_str(f"o {mesh.name}\ng {mesh.name}\n\n")

            for polygon in mesh.polygons:
                v1 = offset + polygon.v1
                v2 = offset + polygon.v2
                v3 = offset + polygon.v3
                self._write_str(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
            self._write_str("\n")

            # Vertex id in mcsa are local to each mesh.
            offset += len(mesh.vertices)

    def _ensure_unique_names(self):
        name_counts: Dict[str, int] = {}

        # Checking names for uniqueness
        for index, mesh in enumerate(self.data.model.meshes):
            name = mesh.name

            # Set default count for name if not present
            name_counts.setdefault(name, 0)

            # Increment count for current name
            name_counts[name] += 1
            count = name_counts[name]

            # If name already taken set name with count
            if count > 1:
                mesh.name = f"{name}_{count}"

            # If name is empty set "noname" with 1-based index
            if not name:
                mesh.name = f"noname_{index + 1}"

    def _vertices(self) -> Generator[Vertex, Any, Any]:
        for mesh in self.data.model.meshes:
            for vertex in mesh.vertices:
                yield vertex
