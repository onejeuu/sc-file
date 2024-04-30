from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder

from scfile.enums import StructFormat as F

# ! IN PROGRESS


class Ms3dBinEncoder(FileEncoder[ModelData]):
    MAX_MS3D_VERTICES = 65534
    MAX_MS3D_TRIANGLES = 65534
    MAX_MS3D_GROUPS = 127
    MAX_MS3D_JOINTS = 127

    def serialize(self):
        self.model = self.data.model
        self.flags = self.data.model.flags

        self.offset = 0
        self.model.ensure_unique_names()

        self.b.writes("MS3D000000")
        self.b.writeb(F.I32, 0x4)

        self.cur_mesh = self.model.meshes[0]
        self.b.writeb(F.U16, len(self.cur_mesh.vertices))

        self.cur_vert_id = 0
        for v in self.cur_mesh.vertices:
            self.b.writeb(F.I8, 0)  # flags
            self.b.writeb(F.F32, v.position.x)
            self.b.writeb(F.F32, v.position.y)
            self.b.writeb(F.F32, v.position.z)

            self.b.writeb(F.U8, 0xFF)

            self.b.writeb(F.U8, self.cur_vert_id + 1)
            self.cur_vert_id += 1

        self.b.writeb(F.U16, len(self.cur_mesh.polygons))

        self.cnt = 0
        for p in self.cur_mesh.polygons:
            self.b.writeb(F.U16, 0)  # flags

            # tmp_word:=word(p.v1)+word(cnt);
            self.b.writeb(F.U16, p.a - 1 + self.cnt)
            self.b.writeb(F.U16, p.b - 1 + self.cnt)
            self.b.writeb(F.U16, p.c - 1 + self.cnt)

            self.b.writeb(F.F32, self.cur_mesh.vertices[p.a - 1].normals.x)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.a - 1].normals.y)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.a - 1].normals.z)

            self.b.writeb(F.F32, self.cur_mesh.vertices[p.b - 1].normals.x)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.b - 1].normals.y)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.b - 1].normals.z)

            self.b.writeb(F.F32, self.cur_mesh.vertices[p.c - 1].normals.x)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.c - 1].normals.y)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.c - 1].normals.z)

            self.b.writeb(F.F32, self.cur_mesh.vertices[p.a - 1].texture.u)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.b - 1].texture.u)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.c - 1].texture.u)

            self.b.writeb(F.F32, self.cur_mesh.vertices[p.a - 1].texture.v)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.b - 1].texture.v)
            self.b.writeb(F.F32, self.cur_mesh.vertices[p.c - 1].texture.v)

            self.b.writeb(F.I8, 1)  # smoothing group
            self.b.writeb(F.I8, 0)  # id of mesh

        self.b.writeb(F.U16, 1)  # meshes count
        # material name
        for x in range(31):
            self.b.writeb(F.I8, 0)

        # ambient
        self.b.writeb(F.F32, 0.2)
        self.b.writeb(F.F32, 0.2)
        self.b.writeb(F.F32, 0.2)
        self.b.writeb(F.F32, 1.0)

        # diffuse
        self.b.writeb(F.F32, 0.8)
        self.b.writeb(F.F32, 0.8)
        self.b.writeb(F.F32, 0.8)
        self.b.writeb(F.F32, 1.0)

        # specular
        self.b.writeb(F.F32, 0.0)
        self.b.writeb(F.F32, 0.0)
        self.b.writeb(F.F32, 0.0)
        self.b.writeb(F.F32, 1.0)

        # emissive
        self.b.writeb(F.F32, 0.0)
        self.b.writeb(F.F32, 0.0)
        self.b.writeb(F.F32, 0.0)
        self.b.writeb(F.F32, 1.0)

        # shininess
        self.b.writeb(F.F32, 0.0)

        # transparency
        self.b.writeb(F.F32, 1.0)

        # mode
        self.b.writeb(F.I8, 0)

        # texture
        for x in range(127):
            self.b.writeb(F.I8, 0)

        # alphamap
        for x in range(127):
            self.b.writeb(F.I8, 0)

        # fAnimationFPS
        self.b.writeb(F.F32, 24)

        # fCurrentTime
        self.b.writeb(F.F32, 1)

        # iTotalFrames
        self.b.writeb(F.F32, 30)

        # skeleton
        self.b.writeb(F.U16, 0)

        # sub-version
        self.b.writeb(F.I32, 1)

        # number of group comments
        self.b.writeb(F.I32, 0)

        # number of material comments
        self.b.writeb(F.I32, 0)

        # number of joint comments
        self.b.writeb(F.I32, 0)

        # model comments presence
        self.b.writeb(F.I32, 0)

        # vertex comments sub-version
        self.b.writeb(F.I32, 2)

        for v in self.cur_mesh.vertices:
            self.b.writeb(F.U8, 0xFF)
            self.b.writeb(F.U8, 0xFF)
            self.b.writeb(F.U8, 0xFF)

            self.b.writeb(F.U8, 0)
            self.b.writeb(F.U8, 0)
            self.b.writeb(F.U8, 0)

            self.b.writeb(F.I32, 0)
