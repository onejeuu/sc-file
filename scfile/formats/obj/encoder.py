from typing import override

import numpy as np

from scfile.content import models as S
from scfile.content.models import Feature
from scfile.content.models import transforms as T
from scfile.core import ModelEncoder
from scfile.enums import ByteOrder, FileFormat

from . import faces


class ObjEncoder(ModelEncoder):
    format = FileFormat.OBJ
    order = ByteOrder.LITTLE

    features = (
        Feature.UV,
        Feature.NORMALS,
    )
    transforms = T.scene_transforms(T.unique_names, T.flip_uv)

    @override
    def _serialize(self):
        self._add_meshes()

    def _add_meshes(self):
        offset = 1

        for mesh in self.data.scene.meshes:
            self.io.string(f"o {mesh.name}\n")
            self.io.string(f"usemtl {mesh.material}\n")

            self._add_geometric_vertices(mesh)

            if self.includes(Feature.UV) and mesh.uv1.size:
                self._add_texture_coordinates(mesh)

            if self.includes(Feature.NORMALS) and mesh.normals.size:
                self._add_vertex_normals(mesh)

            self.io.string(f"g {mesh.name}\n")
            self._add_polygonal_faces(mesh, offset)

            offset += len(mesh.vertices)

    def _vectorize(self, template: bytes, data: np.ndarray, count: int):
        return (template * count) % tuple(data.ravel().tolist())

    def _add_geometric_vertices(self, mesh: S.ModelMesh):
        template = b"v %.6f %.6f %.6f\n"
        self.io.write(self._vectorize(template, mesh.vertices, len(mesh.vertices)))
        self.io.write(b"\n")

    def _add_texture_coordinates(self, mesh: S.ModelMesh):
        template = b"vt %.6f %.6f\n"
        self.io.write(self._vectorize(template, mesh.uv1, len(mesh.vertices)))
        self.io.write(b"\n")

    def _add_vertex_normals(self, mesh: S.ModelMesh):
        template = b"vn %.6f %.6f %.6f\n"
        self.io.write(self._vectorize(template, mesh.normals, len(mesh.vertices)))
        self.io.write(b"\n")

    def _add_polygonal_faces(self, mesh: S.ModelMesh, offset: int):
        flags = faces.Flags(
            uv=self.includes(Feature.UV) and bool(mesh.uv1.size),
            normals=self.includes(Feature.NORMALS) and bool(mesh.normals.size),
        )
        template = faces.TEMPLATE[flags]

        polygons = mesh.polygons + offset
        indices = np.repeat(polygons, 1 + flags.uv + flags.normals)
        self.io.write(self._vectorize(template, indices, len(polygons)))
        self.io.write(b"\n" if len(polygons) else b"\n\n")
