from scfile.consts import McsaModel
from scfile.enums import StructFormat as F
from scfile.file.base import FileEncoder
from scfile.file.data import ModelData


class Ms3dBinEncoder(FileEncoder[ModelData]):
    def serialize(self):
        self.model = self.data.model
        self.meshes = self.data.model.meshes
        self.skeleton = self.data.model.skeleton

        self.model.ensure_unique_names()
        self.model.convert_polygons_to_global()
        self.skeleton.convert_to_local()

        self._add_header()
        self._add_vertices()
        self._add_triangles()
        self._add_groups()
        self._add_materials()
        self._add_joints()

    def _add_header(self):
        self.b.writes("MS3D000000")  # 10 bytes signature
        self.b.writeb(F.I32, 0x4)  # version

    def _add_vertices(self):
        self.b.writeb(F.U16, self.model.total_vertices)

        for mesh in self.meshes:
            for v in mesh.vertices:
                pos = v.position
                # i8 flags, f32 pos[3], i8 bone id, u8 reference count
                # TODO: reference count
                self.b.writeb(F.I8 + (F.F32 * 3) + F.I8 + F.U8, 0, pos.x, pos.y, pos.z, -1, 0xFF)

    def _add_triangles(self):
        self.b.writeb(F.U16, self.model.total_polygons)

        for index, mesh in enumerate(self.meshes):
            for p, gp in zip(mesh.polygons, mesh.global_polygons):
                v1 = mesh.vertices[p.a]
                v2 = mesh.vertices[p.b]
                v3 = mesh.vertices[p.c]

                # ! its awful but faster
                # u16 flags, u16 indices[3]
                # f32 normals[3][3], f32 textures u[3], f32 textures v[3]
                # u8 smoothing group, u8 group index
                self.b.writeb(
                    F.U16
                    + (F.U16 * 3)
                    + (F.F32 * 3)
                    + (F.F32 * 3)
                    + (F.F32 * 3)
                    + (F.F32 * 3)
                    + (F.F32 * 3)
                    + F.U8
                    + F.U8,
                    0,
                    gp.a,
                    gp.b,
                    gp.c,
                    v1.normals.x,
                    v1.normals.y,
                    v1.normals.z,
                    v2.normals.x,
                    v2.normals.y,
                    v2.normals.z,
                    v3.normals.x,
                    v3.normals.y,
                    v3.normals.z,
                    v1.texture.u,
                    v2.texture.u,
                    v3.texture.u,
                    v1.texture.v,
                    v2.texture.v,
                    v3.texture.v,
                    1,
                    index,
                )

    def _add_groups(self):
        self.b.writeb(F.U16, len(self.meshes))  # groups count

        offset = 0

        for index, mesh in enumerate(self.meshes):
            self.b.writeb(F.U8, 0)  # flags
            self.b.write(self._fixedlen(mesh.name))  # group name

            self.b.writeb(F.U16, mesh.count.polygons)  # triangles count

            for p in range(len(mesh.polygons)):
                self.b.writeb(F.U16, p + offset)  # triangles indexes

            self.b.writeb(F.I8, index)  # material index

            offset += len(mesh.polygons)

    def _add_materials(self):
        self.b.writeb(F.U16, len(self.meshes))  # materials count

        for mesh in self.meshes:
            self.b.write(self._fixedlen(mesh.material))  # material name
            self.b.writeb(F.F32 * 4, 0.2, 0.2, 0.2, 1.0)  # ambient rgba
            self.b.writeb(F.F32 * 4, 0.8, 0.8, 0.8, 1.0)  # diffuse rgba
            self.b.writeb(F.F32 * 4, 0.0, 0.0, 0.0, 1.0)  # specular rgba
            self.b.writeb(F.F32 * 4, 0.0, 0.0, 0.0, 1.0)  # emissive rgba
            self.b.writeb(F.F32, 0.0)  # shininess
            self.b.writeb(F.F32, 1.0)  # transparency
            self.b.writeb(F.I8, 1)  # mode
            self.b.writen(count=128, size=1)  # texture
            self.b.writen(count=128, size=1)  # alphamap

    def _add_joints(self):
        self.b.writeb(F.F32, 24)  # fps
        self.b.writeb(F.F32, 1)  # current frame
        self.b.writeb(F.F32, 30)  # total frames

        self.b.writeb(F.U16, len(self.skeleton.bones))

        for bone in self.skeleton.bones:
            self.b.writeb(F.U8, 0)  # flags
            self.b.write(self._fixedlen(bone.name))  # bone name

            parent = self.skeleton.bones[bone.parent_id].name
            parent_name = parent if bone.parent_id != McsaModel.ROOT_BONE_ID else ""

            self.b.write(self._fixedlen(parent_name))  # parent name

            rot = bone.rotation
            pos = bone.position
            self.b.writeb(F.F32 * 3, rot.x, rot.y, rot.z)  # rotation
            self.b.writeb(F.F32 * 3, pos.x, pos.y, pos.z)  # position

            self.b.writeb(F.U16, 0)  # count keyframes rotation
            self.b.writeb(F.U16, 0)  # count keyframes transition

    def _fixedlen(self, name: str) -> bytes:
        return name.encode("utf-8").ljust(32, b"\x00")
