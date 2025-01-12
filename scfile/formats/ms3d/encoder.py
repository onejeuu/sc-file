from scfile.consts import FileSignature, McsaModel
from scfile.core import FileEncoder, ModelContext
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F


VERSION = 0x4


def fixedlen(name: str) -> bytes:
    return name.encode("utf-8").ljust(32, b"\x00")


class Ms3dEncoder(FileEncoder[ModelContext]):
    signature = FileSignature.MS3D

    @property
    def format(self):
        return FileFormat.MS3D

    def prepare(self):
        self.ctx.scene.ensure_unique_names()
        self.ctx.scene.convert_polygons_to_global()
        self.ctx.skeleton.convert_to_local()

    def serialize(self):
        self.b.writeb(F.I32, VERSION)  # version
        self.add_vertices()
        self.add_triangles()
        self.add_groups()
        self.add_materials()
        self.add_joints()

    def add_vertices(self):
        self.b.writeb(F.U16, self.ctx.scene.total_vertices)

        # i8 flags, f32 pos[3], i8 bone id, u8 reference count
        fmt = f"{F.I8}{F.F32 * 3}{F.I8}{F.U8}"

        for mesh in self.ctx.meshes:
            for v in mesh.vertices:
                # TODO: bone id & reference count
                self.b.writeb(fmt, 0, *v.position, McsaModel.ROOT_BONE_ID, 0xFF)

    def add_triangles(self):
        self.b.writeb(F.U16, self.ctx.scene.total_polygons)

        # u16 flags, u16 indices[3]
        # f32 normals[3][3], f32 textures u[3], f32 textures v[3]
        # u8 smoothing group, u8 group index
        fmt = f"{F.U16 * 4}{F.F32 * 15}{F.U8 * 2}"

        for index, mesh in enumerate(self.ctx.meshes):
            for p, gp in zip(mesh.polygons, mesh.global_polygons):
                v1 = mesh.vertices[p.a]
                v2 = mesh.vertices[p.b]
                v3 = mesh.vertices[p.c]
                uv = [v1.texture.u, v2.texture.u, v3.texture.u, v1.texture.v, v2.texture.v, v3.texture.v]
                self.b.writeb(fmt, 0, *gp, *v1.normals, *v2.normals, *v3.normals, *uv, 1, index)

    def add_groups(self):
        self.b.writeb(F.U16, len(self.ctx.meshes))  # groups count

        offset = 0

        for index, mesh in enumerate(self.ctx.meshes):
            self.b.writeb(F.U8, 0)  # flags
            self.b.write(fixedlen(mesh.name))  # group name

            self.b.writeb(F.U16, mesh.count.polygons)  # triangles count

            for p in range(len(mesh.polygons)):
                self.b.writeb(F.U16, p + offset)  # triangles indexes

            self.b.writeb(F.I8, index)  # material index

            offset += len(mesh.polygons)

    def add_materials(self):
        self.b.writeb(F.U16, len(self.ctx.meshes))  # materials count

        # f32 ambient[4], diffuse[4], specular[4], emissive[4] (RGBA)
        # f32 shininess, f32 transparency, i8 mode
        fmt = f"{F.F32 * 18}{F.I8}"

        # rgba templates
        empty = (0.0, 0.0, 0.0, 1.0)
        diffuse = (0.8, 0.8, 0.8, 1.0)

        for mesh in self.ctx.meshes:
            self.b.write(fixedlen(mesh.material))  # material name
            self.b.writeb(fmt, *empty, *diffuse, *empty, *empty, 0.0, 1.0, 1)
            self.b.writenull(size=128)  # texture
            self.b.writenull(size=128)  # alphamap

    def add_joints(self):
        # f32 fps, f32 frame, f32 framesCount, u16 bonesCount
        fmt = f"{F.F32 * 3}{F.U16}"
        self.b.writeb(fmt, 24, 1, 30, len(self.ctx.skeleton.bones))

        for bone in self.ctx.skeleton.bones:
            self.b.writeb(F.U8, 0)  # flags
            self.b.write(fixedlen(bone.name))  # bone name

            parent = self.ctx.skeleton.bones[bone.parent_id].name
            parent_name = parent if bone.parent_id != McsaModel.ROOT_BONE_ID else ""
            self.b.write(fixedlen(parent_name))  # parent name

            # f32 rotation[3], f32 position[3], u16 rotation keyframes, u16 keyframes transition
            fmt = f"{F.F32 * 6}{F.U16 * 2}"
            self.b.writeb(fmt, *bone.rotation, *bone.position, 0, 0)
