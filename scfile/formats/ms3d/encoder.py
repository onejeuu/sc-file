import numpy as np

from scfile.consts import FileSignature, McsaModel
from scfile.core import FileEncoder
from scfile.core.context import ModelContent
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F
from scfile.formats.mcsa.flags import Flag
from scfile.structures.skeleton import euler_to_quat

from .io import Ms3dFileIO


VERSION = 4
COMMENTS_VERSION = 1
VERTEX_EXTRA_VERSION = 1

MAX_VERTICES = 0xFFFF
MAX_TRIANGLES = 0xFFFF


def fixedlen(name: str) -> bytes:
    return name.encode("utf-8").ljust(32, b"\x00")


class Ms3dEncoder(FileEncoder[ModelContent], Ms3dFileIO):
    format = FileFormat.MS3D
    signature = FileSignature.MS3D

    @property
    def skeleton_presented(self) -> bool:
        return self.data.flags[Flag.SKELETON] and self.options.parse_skeleton

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self.skeleton_presented:
            self.data.skeleton.convert_to_local()

    def serialize(self):
        self.writeb(F.I32, VERSION)
        self.add_vertices()
        self.add_triangles()
        self.add_groups()
        self.add_materials()
        self.add_bones()
        self.add_comments()
        self.add_links()

    def add_vertices(self):
        # vertices count
        self.writecount("vertices", self.data.scene.total_vertices, MAX_VERTICES)

        # i8 flags, f32 pos[3], i8 bone id, u8 reference count
        fmt = f"{F.I8}{F.F32 * 3}{F.I8}{F.U8}"

        reference_count = 0xFF  # ? necessary only for optimization, calculation too expensive

        # TODO: links reshape in decoder
        for mesh in self.data.meshes:
            links_ids = mesh.links_ids.astype(F.I8)
            for index, xyz in enumerate(mesh.positions):
                bone_id = links_ids[index * 4] if self.skeleton_presented else McsaModel.ROOT_BONE_ID
                self.writeb(fmt, 0, *xyz, bone_id, reference_count)

    def add_triangles(self):
        # polygons count
        self.writecount("polygons", self.data.scene.total_polygons, MAX_TRIANGLES)

        # u16 flags, u16 indices[3]
        # f32 normals[3][3], f32 textures u[3], f32 textures v[3]
        # u8 smoothing group, u8 group index
        fmt = f"{F.U16 * 4}{F.F32 * 15}{F.U8 * 2}"

        offset = 0
        for index, mesh in enumerate(self.data.meshes):
            for abc in mesh.polygons:
                normals = [i for vertex in abc for i in mesh.normals[vertex]]
                uv = [i for vertex in abc for i in mesh.textures[vertex]]
                indices = (abc + offset).astype(F.U16)

                self.writeb(fmt, 0, *indices, *normals, *uv, 1, index)

            offset += mesh.count.vertices

    def add_groups(self):
        self.writeb(F.U16, len(self.data.meshes))  # groups count

        offset = 0
        for index, mesh in enumerate(self.data.meshes):
            self.writeb(F.U8, 0)  # flags
            self.write(fixedlen(mesh.name))  # group name

            count = mesh.count.polygons
            self.writeb(F.U16, count)  # triangles count
            self.writeb(f"{count}{F.U16}", *np.arange(count, dtype=F.U16) + offset)  # indices
            self.writeb(F.I8, index)  # material index

            offset += count

    def add_materials(self):
        self.writeb(F.U16, len(self.data.meshes))  # materials count

        # f32 ambient[4], diffuse[4], specular[4], emissive[4] (RGBA)
        # f32 shininess, f32 transparency, i8 mode
        fmt = f"{F.F32 * 18}{F.I8}"

        # rgba templates
        empty = (0.0, 0.0, 0.0, 1.0)
        diffuse = (0.8, 0.8, 0.8, 1.0)

        for mesh in self.data.meshes:
            self.write(fixedlen(mesh.material))  # material name
            self.writeb(fmt, *empty, *diffuse, *empty, *empty, 0.0, 1.0, 1)
            self.writenull(size=128)  # texture
            self.writenull(size=128)  # alphamap

    def add_bones(self):
        # f32 fps, f32 frame, f32 framesCount, u16 bonesCount
        fmt = f"{F.F32 * 3}{F.U16}"
        self.writeb(fmt, 24, 1, 30, self.data.count.bones)

        for bone in self.data.skeleton.bones:
            self.writeb(F.U8, 0)  # flags
            self.write(fixedlen(bone.name))  # bone name

            parent = self.data.skeleton.bones[bone.parent_id]
            parent_name = parent.name if bone.parent_id != McsaModel.ROOT_BONE_ID else ""
            self.write(fixedlen(parent_name))  # parent name

            # f32 bone rotation[3], f32 bone position[3]
            # u16 keyframes rotations, u16 keyframes transitions
            fmt = f"{F.F32 * 6}{F.U16 * 2}"

            qx, qy, qz, qw = euler_to_quat(bone.rotation)
            self.writeb(fmt, qx, qy, qz, *bone.position, 0, 0)

    def add_comments(self):
        self.writeb(F.I32, COMMENTS_VERSION)  # comments version
        fmt = F.U32 * 4  # u32 group, u32 material, u32 joints, u32 model
        self.writeb(fmt, 0, 0, 0, 0)  # comments count

    def add_links(self):
        self.writeb(F.I32, VERTEX_EXTRA_VERSION)  # vertex extra version

        # i8 ids[3], u8 weights[3]
        fmt = f"{F.I8 * 3}{F.U8 * 3}"

        # TODO: links reshape in decoder
        for mesh in self.data.meshes:
            links_ids = mesh.links_ids.astype(F.I8).reshape(-1, 4)
            links_weights = (mesh.links_weights * 255).astype(F.U8).reshape(-1, 4)
            for ids, weights in zip(links_ids, links_weights):
                self.writeb(fmt, *ids[:3], *weights[:3])
