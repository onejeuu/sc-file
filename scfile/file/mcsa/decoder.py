import numpy as np

from scfile import exceptions as exc
from scfile.consts import Factor, McsaSize, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.file.data import ModelData
from scfile.file.decoder import FileDecoder
from scfile.file.obj.encoder import ObjEncoder
from scfile.io.mcsa import McsaFileIO
from scfile.utils.model import Bone, Mesh, Model, Vector, VertexBone

from .flags import Flag, McsaFlags
from .versions import SUPPORTED_VERSIONS, VERSION_FLAGS


class McsaDecoder(FileDecoder[McsaFileIO, ModelData]):
    def to_obj(self):
        return self.convert_to(ObjEncoder)

    @property
    def opener(self):
        return McsaFileIO

    @property
    def order(self):
        return ByteOrder.LITTLE

    @property
    def signature(self):
        return Signature.MCSA

    def create_data(self):
        return ModelData(self.model)

    def parse(self):
        self._create_model()
        self._parse_header()
        self._parse_meshes()
        self._parse_skeleton()

    def _create_model(self):
        self.model = Model()

    def _parse_header(self):
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self):
        self.version = self.f.readb(F.F32)

        if self.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

    def _parse_flags(self):
        self.flags = McsaFlags()
        self.flags_count = VERSION_FLAGS.get(self.version)

        if not self.flags_count:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

        for index in range(self.flags_count):
            self.flags[index] = self.f.readb(F.BOOL)

        self.model.flags.texture = self.flags[Flag.TEXTURE]
        self.model.flags.normals = self.flags[Flag.NORMALS]

    def _parse_scales(self):
        self.model.scale.position = self.f.readb(F.F32)

        if self.flags[Flag.TEXTURE]:
            self.model.scale.texture = self.f.readb(F.F32)

        # ! unconfirmed
        if self.flags[Flag.NORMALS] and self.version >= 10.0:
            self.model.scale.normals = self.f.readb(F.F32)

    def _parse_meshes(self):
        self.meshes_count = self.f.readb(F.U32)

        for _ in range(self.meshes_count):
            self._parse_mesh()

    def _parse_mesh(self):
        self.mesh = Mesh()

        # Name & Material
        self.mesh.name = self.f.reads().decode()
        self.mesh.material = self.f.reads().decode()

        # Skeleton bone indexes
        if self.flags[Flag.SKELETON]:
            self._parse_bone_indexes()

        # Counts
        self.count.vertices = self.f.readcounts()
        self.count.polygons = self.f.readcounts()
        self.mesh.resize()

        # ! unknown, unconfirmed
        if self.flags[Flag.TEXTURE]:
            self.model.scale.weight = self.f.readb(F.F32)

        # ! unconfirmed
        if self.version >= 10.0:
            self._parse_locals()

        # Geometric vertices
        self._parse_position()

        # Texture vertices
        if self.flags[Flag.TEXTURE]:
            self._parse_texture()

        # ! unconfirmed
        if self.flags[Flag.BITANGENTS]:
            self._skip_vertices(size=4)

        # Vertex normals
        if self.flags[Flag.NORMALS]:
            self._parse_normals()

        # ! unconfirmed
        if self.flags[Flag.TANGENTS]:
            self._skip_vertices(size=4)

        # Skeleton bones
        if self.flags[Flag.SKELETON]:
            self._parse_bones()

        # Vertex colors
        if self.flags[Flag.COLORS]:
            self._parse_colors()

        # Polygon faces
        self._parse_polygons()

        self.model.meshes.append(self.mesh)

    @property
    def count(self):
        return self.mesh.count

    @property
    def vertices(self):
        return self.mesh.vertices

    @property
    def scale(self):
        return self.model.scale

    def _parse_bone_indexes(self):
        self.count.links = self.f.readb(F.U8)
        self.count.bones = self.f.readb(F.U8)

        for index in range(self.count.bones):
            self.mesh.bones[index] = self.f.readb(F.I8)

    def _parse_locals(self):
        # Possibly local axis and center (6 floats)
        # Quite useless
        self.f.read(6 * 4)

    def _read_vertex_data(self, fmt: str, factor: float, size: int, scale: float = 1.0):
        data = self.f.readvalues(fmt=fmt, size=size, count=self.count.vertices)

        scaled = np.array(data) * scale / factor
        reshaped = scaled.reshape(-1, size)

        return reshaped

    def _parse_position(self):
        xyzw = self._read_vertex_data(F.I16, Factor.I16, McsaSize.POSITION, self.scale.position)

        for vertex, (x, y, z, _) in zip(self.vertices, xyzw):
            vertex.position.x = x
            vertex.position.y = y
            vertex.position.z = z

    def _parse_texture(self):
        uv = self._read_vertex_data(F.I16, Factor.I16, McsaSize.TEXTURE, self.scale.texture)

        for vertex, (u, v) in zip(self.vertices, uv):
            vertex.texture.u = u
            vertex.texture.v = v

    def _parse_normals(self):
        xyzw = self._read_vertex_data(F.I8, Factor.I8, McsaSize.NORMALS)

        for vertex, (x, y, z, _) in zip(self.vertices, xyzw):
            vertex.normals.x = x
            vertex.normals.y = y
            vertex.normals.z = z

    def _skip_vertices(self, size: int = 4):
        self.f.read(self.count.vertices * size)

    def _parse_bones(self):
        match self.count.links:
            case 0:
                pass
            case 1 | 2:
                self._parse_bone_packed()
            case 3 | 4:
                self._parse_bone_plains()
            case _:
                raise exc.McsaUnknownLinkCount(self.path, self.count.links)

    def _parse_bone_packed(self):
        for v in self.mesh.vertices:
            v.bone = VertexBone()
            for i in range(2):
                v.bone.ids[i] = self.mesh.bones[self.f.readb(F.U8)]
            for i in range(2):
                v.bone.weights[i] = self.f.readb(F.U8) / 255

    def _parse_bone_plains(self):
        for v in self.mesh.vertices:
            v.bone = VertexBone()
            for i in range(4):
                v.bone.ids[i] = self.mesh.bones[self.f.readb(F.U8)]
            for i in range(4):
                v.bone.weights[i] = self.f.readb(F.U8) / 255

    def _parse_colors(self):
        # Quite useless
        self._skip_vertices(size=4)
        return

        # Could be rgba, but not that important
        argb = self._read_vertex_data(F.U8, Factor.U8, McsaSize.COLOR)

        for vertex, (_, r, g, b) in zip(self.vertices, argb):
            vertex.color.r = r
            vertex.color.g = g
            vertex.color.b = b

    def _read_polygons_data(self):
        size = McsaSize.POLYGONS
        count = self.count.polygons * size
        fmt = F.U16 if count < Factor.U16 else F.U32

        data = self.f.readvalues(fmt=fmt, size=size, count=self.count.polygons)

        # In mcsa vertex indexes 0-based
        shifted = np.array(data) + 1
        reshaped = shifted.reshape(-1, size)

        return reshaped

    def _parse_polygons(self):
        abc = self._read_polygons_data()

        for polygon, (a, b, c) in zip(self.mesh.polygons, abc):
            polygon.a = a
            polygon.b = b
            polygon.c = c

    def _parse_skeleton(self):
        self.model.skeleton.bones = [Bone() for _ in range(self.f.readb(F.U8))]

        for bone in self.model.skeleton.bones:
            i = self.model.skeleton.bones.index(bone)
            bone.name = self.f.reads().decode()
            bone.parent_id = self.f.readb(F.U8)
            if bone.parent_id == self.model.skeleton.bones.index(bone):
                bone.parent_id = -1
            bone.position = Vector()
            bone.position.x = self.f.readb(F.F32)
            bone.position.y = self.f.readb(F.F32)
            bone.position.z = self.f.readb(F.F32)
            bone.rotation.x = self.f.readb(F.F32)
            bone.rotation.y = self.f.readb(F.F32)
            bone.rotation.z = self.f.readb(F.F32)
            self.model.skeleton.bones[i] = bone

        self._convert_skeleton_to_local()

    def _convert_skeleton_to_local(self):
        parent_id = 0
        bones = self.model.skeleton.bones
        for b in bones:
            b.rotation = Vector()
            parent_id = b.parent_id
            while parent_id >= 0:
                b.position.sub(bones[parent_id].position)
                parent_id = self.model.skeleton.bones[parent_id].parent_id

            
