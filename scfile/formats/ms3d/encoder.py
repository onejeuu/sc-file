import numpy as np

from scfile.consts import FileSignature, ModelDefaults
from scfile.core import FileEncoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.models import transforms as T

from .io import Ms3dFileIO


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


class Ms3dEncoder(FileEncoder[ModelContent], Ms3dFileIO):
    content_type = ModelContent
    format = FileFormat.MS3D
    signature = FileSignature.MS3D
    order = ByteOrder.LITTLE

    transforms = [T.unique_names, T.skeleton_to_local]

    def serialize(self):
        self._writeb(F.I32, VERSION)
        self._add_vertices()
        self._add_triangles()
        self._add_groups()
        self._add_materials()
        self._add_bones()
        self._add_comments()
        self._add_links()

    def _add_vertices(self):
        # vertices count
        self._writecount("vertices", self.data.scene.total_vertices, MAX_VERTICES)

        reference_count = 0xFF  # ? necessary only for optimization, calculation too expensive

        for mesh in self.data.scene.meshes:
            vertices = np.empty(len(mesh.vertices), dtype=VERTEX_DTYPE)
            vertices["flags"] = 0
            vertices["position"] = mesh.vertices
            vertices["bone_id"] = mesh.links_ids[:, 0] if self._skeleton_presented else ModelDefaults.ROOT_BONE_ID
            vertices["reference_count"] = reference_count
            self.write(vertices.tobytes())

    def _add_triangles(self):
        # polygons count
        self._writecount("polygons", self.data.scene.total_polygons, MAX_TRIANGLES)

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
            self.write(triangles.tobytes())

            offset += len(mesh.vertices)

    def _add_groups(self):
        self._writeb(F.U16, len(self.data.scene.meshes))  # groups count

        offset = 0
        for index, mesh in enumerate(self.data.scene.meshes):
            self._writeb(F.U8, 0)  # flags
            self._writefixedstring(mesh.name)  # group name

            count = len(mesh.polygons)
            self._writeb(F.U16, count)  # triangles count
            indices = np.arange(offset, offset + count, dtype="<u2")
            self.write(indices.tobytes())
            self._writeb(F.I8, index)  # material index

            offset += count

    def _add_materials(self):
        self._writeb(F.U16, len(self.data.scene.meshes))  # materials count

        # f32 ambient[4], diffuse[4], specular[4], emissive[4] (RGBA)
        # f32 shininess, f32 transparency, i8 mode
        fmt = f"{F.F32 * 18}{F.I8}"

        # rgba templates
        empty = (0.0, 0.0, 0.0, 1.0)
        diffuse = (0.8, 0.8, 0.8, 1.0)

        for mesh in self.data.scene.meshes:
            self._writefixedstring(mesh.material)  # material name
            self._writeb(fmt, *empty, *diffuse, *empty, *empty, 0.0, 1.0, 1)
            self._writenull(size=128)  # texture
            self._writenull(size=128)  # alphamap

    def _add_bones(self):
        # f32 fps, f32 frame, f32 framesCount, u16 bonesCount
        fmt = f"{F.F32 * 3}{F.U16}"
        self._writeb(fmt, 24, 1, 30, len(self.data.scene.skeleton.bones))

        for bone in self.data.scene.skeleton.bones:
            self._writeb(F.U8, 0)  # flags
            self._writefixedstring(bone.name)  # bone name

            parent = self.data.scene.skeleton.bones[bone.parent_id]
            parent_name = parent.name if bone.parent_id != ModelDefaults.ROOT_BONE_ID else ""
            self._writefixedstring(parent_name)  # parent name

            # f32 bone rotation[3], f32 bone position[3]
            # u16 keyframes rotations, u16 keyframes transitions
            fmt = f"{F.F32 * 6}{F.U16 * 2}"

            qx, qy, qz, qw = bone.quaternion
            self._writeb(fmt, qx, qy, qz, *bone.position, 0, 0)

    def _add_comments(self):
        self._writeb(F.I32, COMMENTS_VERSION)  # comments version
        fmt = F.U32 * 4  # u32 group, u32 material, u32 joints, u32 model
        self._writeb(fmt, 0, 0, 0, 0)  # comments count

    def _add_links(self):
        self._writeb(F.I32, VERTEX_EXTRA_VERSION)  # vertex extra version

        # i8 ids[3], u8 weights[3]
        fmt = f"{F.I8 * 3}{F.U8 * 3}"

        for mesh in self.data.scene.meshes:
            links_ids = mesh.links_ids.astype(F.I8)
            links_weights = (mesh.links_weights * 255).astype(F.U8)

            for ids, weights in zip(links_ids, links_weights):
                self._writeb(fmt, *ids[:3], *weights[:3])
