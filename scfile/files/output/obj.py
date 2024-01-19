from dataclasses import dataclass
from typing import Dict, Callable

from scfile.utils.model import Model

from .base import BaseOutputFile, OutputData


@dataclass
class ObjOutputData(OutputData):
    model: Model


class ObjFile(BaseOutputFile[ObjOutputData]):
    def write(self) -> None:
        self.offset = 0
        self._ensure_unique_names()

        for mesh in self.meshes:
            self.mesh = mesh

            self._write_list(self._geometric_vertices())
            self._write_list(self._texture_vertices())
            self._write_list(self._vertex_normals())

            self._write_str(f"g {mesh.name}\n")
            self._write_list(self._polygonal_faces())

    @property
    def meshes(self):
        return self.data.model.meshes

    def _add_material(self) -> None:
        self._write_str(f"mtllib {self.filename}.mtl", "\n\n")

    def _geometric_vertices(self) -> list[str]:
        return self._pack_vertices(
            lambda v: f"v {v.position.x} {v.position.y} {v.position.z}\n"
        )

    def _texture_vertices(self) -> list[str]:
        return self._pack_vertices(
            lambda v: f"vt {v.texture.u} {1.0 - v.texture.v}\n"
        )

    def _vertex_normals(self) -> list[str]:
        return self._pack_vertices(
            lambda v: f"vn {v.normals.i} {v.normals.j} {v.normals.k}\n"
        )

    def _polygonal_faces(self) -> list[str]:
        data: list[str] = []

        for polygon in self.mesh.polygons:
            v1 = polygon.v1 + self.offset
            v2 = polygon.v2 + self.offset
            v3 = polygon.v3 + self.offset
            data.append(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
        data.append("\n")

        # Vertex id in mcsa are local to each mesh.
        self.offset += len(self.mesh.vertices)

        return data

    def _ensure_unique_names(self):
        name_counts: Dict[str, int] = {}

        # Checking names for uniqueness
        for index, mesh in enumerate(self.meshes):
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

    def _pack_vertices(self, func: Callable) -> list[str]:
        data: list[str] = []

        for vertex in self.mesh.vertices:
            data.append(func(vertex))

        data.append("\n")
        return data
