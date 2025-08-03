import numpy as np

from scfile.consts import FileSignature, McsaModel
from scfile.core import FileEncoder, ModelContent
from scfile.enums import F, FileFormat

from .io import Ms3dFileIO


VERSION = 4
COMMENTS_VERSION = 1
VERTEX_EXTRA_VERSION = 1

MAX_VERTICES = 0xFFFF
MAX_TRIANGLES = 0xFFFF


class Ms3dEncoder(FileEncoder[ModelContent], Ms3dFileIO):
    format = FileFormat.MS3D
    signature = FileSignature.MS3D

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self._skeleton_presented:
            self.data.scene.skeleton.convert_to_local()

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

        # i8 flags, f32 pos[3], i8 bone id, u8 reference count
        fmt = f"{F.I8}{F.F32 * 3}{F.I8}{F.U8}"

        reference_count = 0xFF  # ? necessary only for optimization, calculation too expensive

        for mesh in self.data.scene.meshes:
            for index, xyz in enumerate(mesh.positions):
                bone_id = mesh.links_ids.astype(F.I8)[index][0] if self._skeleton_presented else McsaModel.ROOT_BONE_ID
                self._writeb(fmt, 0, *xyz, bone_id, reference_count)

    def _add_triangles(self):
        # polygons count
        self._writecount("polygons", self.data.scene.total_polygons, MAX_TRIANGLES)

        # u16 flags, u16 indices[3]
        # f32 normals[3][3], f32 textures u[3], f32 textures v[3]
        # u8 smoothing group, u8 group index
        fmt = f"{F.U16 * 4}{F.F32 * 15}{F.U8 * 2}"

        offset = 0
        for index, mesh in enumerate(self.data.scene.meshes):
            for abc in mesh.polygons:
                normals = [i for vertex in abc for i in mesh.normals[vertex]]
                uv = np.concatenate([mesh.textures[abc][:, 0], mesh.textures[abc][:, 1]], dtype=F.F32)
                indices = (abc + offset).astype(F.U16)

                self._writeb(fmt, 0, *indices, *normals, *uv, 1, index)

            offset += mesh.count.vertices

    def _add_groups(self):
        self._writeb(F.U16, len(self.data.scene.meshes))  # groups count

        offset = 0
        for index, mesh in enumerate(self.data.scene.meshes):
            self._writeb(F.U8, 0)  # flags
            self._writefixedstring(mesh.name)  # group name

            count = mesh.count.polygons
            self._writeb(F.U16, count)  # triangles count
            self._writeb(f"{count}{F.U16}", *np.arange(count, dtype=F.U16) + offset)  # indices
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
        self._writeb(fmt, 24, 1, 30, self.data.scene.count.bones)

        for bone in self.data.scene.skeleton.bones:
            self._writeb(F.U8, 0)  # flags
            self._writefixedstring(bone.name)  # bone name

            parent = self.data.scene.skeleton.bones[bone.parent_id]
            parent_name = parent.name if bone.parent_id != McsaModel.ROOT_BONE_ID else ""
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
