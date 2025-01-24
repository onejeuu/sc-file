from scfile.consts import FileSignature, McsaModel
from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F


VERSION = 0x4


def fixedlen(name: str) -> bytes:
    return name.encode("utf-8").ljust(32, b"\x00")


class Ms3dEncoder(FileEncoder[ModelContent, ModelOptions]):
    format = FileFormat.MS3D
    signature = FileSignature.MS3D

    _options = ModelOptions

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
        self.add_joints()

    def add_vertices(self):
        self.writeb(F.U16, self.data.scene.total_vertices)

        # i8 flags, f32 pos[3], i8 bone id, u8 reference count
        fmt = f"{F.I8}{F.F32 * 3}{F.I8}{F.U8}"

        for mesh in self.data.meshes:
            for v in mesh.vertices:
                # TODO: bone id & reference count
                self.writeb(fmt, 0, *v.position, McsaModel.ROOT_BONE_ID, 0xFF)

    def add_triangles(self):
        self.writeb(F.U16, self.data.scene.total_polygons)

        # u16 flags, u16 indices[3]
        # f32 normals[3][3], f32 textures u[3], f32 textures v[3]
        # u8 smoothing group, u8 group index
        fmt = f"{F.U16 * 4}{F.F32 * 15}{F.U8 * 2}"

        for index, mesh in enumerate(self.data.meshes):
            for p, gp in zip(mesh.polygons, mesh.faces):
                v1 = mesh.vertices[p.a]
                v2 = mesh.vertices[p.b]
                v3 = mesh.vertices[p.c]
                uv = [v1.texture.u, v2.texture.u, v3.texture.u, v1.texture.v, v2.texture.v, v3.texture.v]
                self.writeb(fmt, 0, *gp, *v1.normals, *v2.normals, *v3.normals, *uv, 1, index)

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

    def add_joints(self):
        # f32 fps, f32 frame, f32 framesCount, u16 bonesCount
        fmt = f"{F.F32 * 3}{F.U16}"
        self.writeb(fmt, 24, 1, 30, len(self.data.skeleton.bones))

        for bone in self.data.skeleton.bones:
            self.writeb(F.U8, 0)  # flags
            self.write(fixedlen(bone.name))  # bone name

            parent = self.data.skeleton.bones[bone.parent_id].name
            parent_name = parent if bone.parent_id != McsaModel.ROOT_BONE_ID else ""
            self.write(fixedlen(parent_name))  # parent name

            # f32 rotation[3], f32 position[3], u16 rotation keyframes, u16 keyframes transition
            fmt = f"{F.F32 * 6}{F.U16 * 2}"
            self.writeb(fmt, *bone.rotation, *bone.position, 0, 0)
