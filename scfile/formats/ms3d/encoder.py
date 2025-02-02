from scfile.consts import FileSignature, McsaModel
from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F
from scfile.exceptions import Ms3dCountsLimit
from scfile.formats.mcsa.flags import Flag
from scfile.geometry.mesh import padded
from scfile.geometry.skeleton import euler_to_quat


VERSION = 4
COMMENTS_VERSION = 1
VERTEX_EXTRA_VERSION = 1

MAX_VERTICES = 0xFFFF
MAX_TRIANGLES = 0xFFFF


def fixedlen(name: str) -> bytes:
    return name.encode("utf-8").ljust(32, b"\x00")


class Ms3dEncoder(FileEncoder[ModelContent, ModelOptions]):
    format = FileFormat.MS3D
    signature = FileSignature.MS3D

    _options = ModelOptions

    @property
    def skeleton_presented(self) -> bool:
        return self.data.flags[Flag.SKELETON] and self.options.parse_skeleton

    def prepare(self):
        self.data.scene.ensure_unique_names()
        self.data.scene.convert_polygons_to_faces()
        self.data.skeleton.convert_to_local()

    def serialize(self):
        self.writeb(F.I32, VERSION)  # version
        self.add_vertices()
        self.add_triangles()
        self.add_groups()
        self.add_materials()
        self.add_bones()
        self.add_comments()
        self.add_links()

    def add_vertices(self):
        count = self.data.scene.total_vertices
        if count > MAX_VERTICES:
            raise Ms3dCountsLimit("vertices", count, MAX_VERTICES)
        self.writeb(F.U16, count)  # vertices count

        # i8 flags, f32 pos[3], i8 bone id, u8 reference count
        fmt = f"{F.I8}{F.F32 * 3}{F.I8}{F.U8}"

        reference_count = 0xFF  # ? necessary only for optimization, calculation too expensive

        if self.skeleton_presented:
            for v in self.data.scene.get_vertices():
                self.writeb(fmt, 0, *v.position, v.bone_ids[0], reference_count)

        else:
            for v in self.data.scene.get_vertices():
                self.writeb(fmt, 0, *v.position, McsaModel.ROOT_BONE_ID, reference_count)

    def add_triangles(self):
        count = self.data.scene.total_polygons
        if count > MAX_TRIANGLES:
            raise Ms3dCountsLimit("polygons", count, MAX_TRIANGLES)
        self.writeb(F.U16, count)  # polygons count

        # u16 flags, u16 indices[3]
        # f32 normals[3][3], f32 textures u[3], f32 textures v[3]
        # u8 smoothing group, u8 group index
        fmt = f"{F.U16 * 4}{F.F32 * 15}{F.U8 * 2}"

        for index, mesh in enumerate(self.data.meshes):
            for p, f in zip(mesh.polygons, mesh.faces):
                v1 = mesh.vertices[p.a]
                v2 = mesh.vertices[p.b]
                v3 = mesh.vertices[p.c]
                uv = [v1.texture.u, v2.texture.u, v3.texture.u, v1.texture.v, v2.texture.v, v3.texture.v]
                self.writeb(fmt, 0, *f, *v1.normals, *v2.normals, *v3.normals, *uv, 1, index)

    def add_groups(self):
        self.writeb(F.U16, len(self.data.meshes))  # groups count

        offset = 0

        for index, mesh in enumerate(self.data.meshes):
            self.writeb(F.U8, 0)  # flags
            self.write(fixedlen(mesh.name))  # group name

            self.writeb(F.U16, mesh.count.polygons)  # triangles count

            for p in range(len(mesh.polygons)):
                self.writeb(F.U16, p + offset)  # triangles indexes

            self.writeb(F.I8, index)  # material index

            offset += len(mesh.polygons)

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
        self.writeb(fmt, 24, 1, 30, len(self.data.skeleton.bones))

        for bone in self.data.skeleton.bones:
            self.writeb(F.U8, 0)  # flags
            self.write(fixedlen(bone.name))  # bone name

            parent = self.data.skeleton.bones[bone.parent_id]
            parent_name = parent.name if bone.parent_id != McsaModel.ROOT_BONE_ID else ""
            self.write(fixedlen(parent_name))  # parent name

            # f32 rotation[3], f32 position[3], u16 rotation keyframes, u16 keyframes transition
            fmt = f"{F.F32 * 6}{F.U16 * 2}"

            qx, qy, qz, qw = euler_to_quat(bone.rotation)
            self.writeb(fmt, qx, qy, qz, *bone.position, 0, 0)

    def add_comments(self):
        self.writeb(F.I32, COMMENTS_VERSION)  # comments version
        fmt = F.U32 * 4  # u32 group, u32 material, u32 joints, u32 model
        self.writeb(fmt, 0, 0, 0, 0)  # comments count

    def add_links(self):
        self.writeb(F.I32, VERTEX_EXTRA_VERSION)  # vertex extra version

        # i8 boneid[3], u8 weights[3]
        fmt = f"{F.I8 * 3}{F.U8 * 3}"

        for mesh in self.data.meshes:
            for v in mesh.vertices:
                self.writeb(
                    fmt,
                    *padded(v.bone_ids, stop=3, default=0),
                    *map(lambda w: int(w * 255), padded(v.bone_weights, stop=3, default=0.0)),
                )
