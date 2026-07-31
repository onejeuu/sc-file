from typing import override

import numpy as np

from scfile.consts import FileSignature
from scfile.core import FileEncoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.io.ms3d import Ms3dWriter
from scfile.structures.models import ROOT_BONE_ID, Feature
from scfile.structures.models import transforms as T


VERSION = 4
COMMENTS_VERSION = 1
VERTEX_EXTRA_VERSION = 1

MAX_VERTICES = 0xFFFF
MAX_TRIANGLES = 0xFFFF

VERTEX_DTYPE = np.dtype(
    [
        ("flags", "i1"),
        ("position", "<f4", 3),
        ("bone_id", "i1"),
        ("reference_count", "u1"),
    ]
)

TRIANGLE_DTYPE = np.dtype(
    [
        ("flags", "<u2"),
        ("indices", "<u2", 3),
        ("normals", "<f4", (3, 3)),
        ("u", "<f4", 3),
        ("v", "<f4", 3),
        ("smoothing_group", "u1"),
        ("group_index", "u1"),
    ]
)


class Ms3dEncoder(FileEncoder[ModelContent, Ms3dWriter]):
    content_type = ModelContent
    format = FileFormat.MS3D
    signature = FileSignature.MS3D
    order = ByteOrder.LITTLE
    io_factory = Ms3dWriter

    features = (
        Feature.UV,
        Feature.NORMALS,
        Feature.SKELETON,
    )
    transforms = T.scene_transforms(T.unique_names, T.skeleton_to_local)

    @override
    def _serialize(self):
        self.io.value(F.I32, VERSION)
        self._add_vertices()
        self._add_triangles()
        self._add_groups()
        self._add_materials()
        self._add_bones()
        self._add_comments()
        self._add_links()

    def _add_vertices(self):
        # vertices count
        self.io.count("vertices", self.data.scene.total_vertices, MAX_VERTICES)

        reference_count = 0xFF  # ? necessary only for optimization, calculation too expensive

        for mesh in self.data.scene.meshes:
            vertices = np.empty(len(mesh.vertices), dtype=VERTEX_DTYPE)
            vertices["flags"] = 0
            vertices["position"] = mesh.vertices
            vertices["bone_id"] = (
                mesh.links_ids[:, 0]
                if self.includes(Feature.SKELETON)
                else ROOT_BONE_ID
            )
            vertices["reference_count"] = reference_count
            self.io.write(vertices.tobytes())

    def _add_triangles(self):
        # polygons count
        self.io.count("polygons", self.data.scene.total_polygons, MAX_TRIANGLES)

        offset = 0
        for index, mesh in enumerate(self.data.scene.meshes):
            triangles = np.empty(len(mesh.polygons), dtype=TRIANGLE_DTYPE)
            uv = mesh.uv1[mesh.polygons]

            triangles["flags"] = 0
            triangles["indices"] = mesh.polygons + offset
            triangles["normals"] = mesh.normals[mesh.polygons]
            triangles["u"] = uv[:, :, 0]
            triangles["v"] = uv[:, :, 1]
            triangles["smoothing_group"] = 1
            triangles["group_index"] = index
            self.io.write(triangles.tobytes())

            offset += len(mesh.vertices)

    def _add_groups(self):
        self.io.value(F.U16, len(self.data.scene.meshes))  # groups count

        offset = 0
        for index, mesh in enumerate(self.data.scene.meshes):
            self.io.value(F.U8, 0)  # flags
            self.io.fixed_string(mesh.name)  # group name

            count = len(mesh.polygons)
            self.io.value(F.U16, count)  # triangles count
            indices = np.arange(offset, offset + count, dtype="<u2")
            self.io.write(indices.tobytes())
            self.io.value(F.I8, index)  # material index

            offset += count

    def _add_materials(self):
        self.io.value(F.U16, len(self.data.scene.meshes))  # materials count

        # f32 ambient[4], diffuse[4], specular[4], emissive[4] (RGBA)
        # f32 shininess, f32 transparency, i8 mode
        fmt = f"{F.F32 * 18}{F.I8}"

        # rgba templates
        empty = (0.0, 0.0, 0.0, 1.0)
        diffuse = (0.8, 0.8, 0.8, 1.0)

        for mesh in self.data.scene.meshes:
            self.io.fixed_string(mesh.material)  # material name
            self.io.value(fmt, *empty, *diffuse, *empty, *empty, 0.0, 1.0, 1)
            self.io.null(size=128)  # texture
            self.io.null(size=128)  # alphamap

    def _add_bones(self):
        bones = self.data.scene.skeleton.bones if self.includes(Feature.SKELETON) else ()

        # f32 fps, f32 frame, f32 framesCount, u16 bonesCount
        fmt = f"{F.F32 * 3}{F.U16}"
        self.io.value(fmt, 24, 1, 30, len(bones))

        for bone in bones:
            self.io.value(F.U8, 0)  # flags
            self.io.fixed_string(bone.name)  # bone name

            parent = self.data.scene.skeleton.bones[bone.parent_id]
            parent_name = parent.name if bone.parent_id != ROOT_BONE_ID else ""
            self.io.fixed_string(parent_name)  # parent name

            # f32 bone rotation[3], f32 bone position[3]
            # u16 keyframes rotations, u16 keyframes transitions
            fmt = f"{F.F32 * 6}{F.U16 * 2}"

            qx, qy, qz, qw = bone.quaternion
            self.io.value(fmt, qx, qy, qz, *bone.position, 0, 0)

    def _add_comments(self):
        self.io.value(F.I32, COMMENTS_VERSION)  # comments version
        fmt = F.U32 * 4  # u32 group, u32 material, u32 joints, u32 model
        self.io.value(fmt, 0, 0, 0, 0)  # comments count

    def _add_links(self):
        self.io.value(F.I32, VERTEX_EXTRA_VERSION)  # vertex extra version

        # i8 ids[3], u8 weights[3]
        fmt = f"{F.I8 * 3}{F.U8 * 3}"

        for mesh in self.data.scene.meshes:
            if self.includes(Feature.SKELETON):
                links_ids = mesh.links_ids.astype(F.I8)
                links_weights = (mesh.links_weights * 255).astype(F.U8)
            else:
                links_ids = np.full(
                    (len(mesh.vertices), 4),
                    ROOT_BONE_ID,
                    dtype=F.I8,
                )
                links_weights = np.zeros((len(mesh.vertices), 4), dtype=F.U8)

            for ids, weights in zip(links_ids, links_weights):
                self.io.value(fmt, *ids[:3], *weights[:3])
