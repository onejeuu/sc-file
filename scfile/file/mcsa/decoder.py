import numpy as np

from scfile import exceptions as exc
from scfile.consts import Factor, McsaSize, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.file.data import ModelData
from scfile.file.decoder import FileDecoder
from scfile.file.obj.encoder import ObjEncoder
from scfile.io.mcsa import McsaFileIO
from scfile.utils.model import Mesh, Model, Vector

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

        flags_count = VERSION_FLAGS.get(self.version)

        if not flags_count:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

        for index in range(flags_count):
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

    def _parse_meshes(self) -> None:
        meshes_count = self.f.readb(F.U32)

        for _ in range(meshes_count):
            self._parse_mesh()

    def _parse_mesh(self) -> None:
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

    def _parse_bone_indexes(self) -> None:
        self.count.links = self.f.readb(F.U8)
        self.count.bones = self.f.readb(F.U8)

        for index in range(self.count.bones):
            self.mesh.bones[index] = self.f.readb(F.I8)

    def _parse_locals(self) -> None:
        self.model.local.axis = Vector(
            self.f.readb(F.F32),
            self.f.readb(F.F32),
            self.f.readb(F.F32),
        )

        self.model.local.center = Vector(
            self.f.readb(F.F32),
            self.f.readb(F.F32),
            self.f.readb(F.F32),
        )

    def _parse_vertex_data(self, fmt: str, factor: float, size: int, scale: float = 1.0):
        data = self.f.readvalues(fmt=fmt, size=size, count=self.count.vertices)

        scaled = np.array(data) * scale / factor
        reshaped = scaled.reshape(-1, size)

        return reshaped

    def _parse_position(self) -> None:
        xyzw = self._parse_vertex_data(F.I16, Factor.I16, McsaSize.POSITION, self.scale.position)

        for vertex, (x, y, z, _) in zip(self.vertices, xyzw):
            vertex.position.x = x
            vertex.position.y = y
            vertex.position.z = z

    def _parse_texture(self) -> None:
        uv = self._parse_vertex_data(F.I16, Factor.I16, McsaSize.TEXTURE, self.scale.texture)

        for vertex, (u, v) in zip(self.vertices, uv):
            vertex.texture.u = u
            vertex.texture.v = v

    def _parse_normals(self) -> None:
        xyzw = self._parse_vertex_data(F.I8, Factor.I8, McsaSize.NORMALS)

        for vertex, (x, y, z, _) in zip(self.vertices, xyzw):
            vertex.normals.x = x
            vertex.normals.y = y
            vertex.normals.z = z

    def _skip_vertices(self, size: int = 4) -> None:
        self.f.read(self.count.vertices * size)

    def _parse_bones(self) -> None:
        match self.count.links:
            case 0:
                pass
            case 1 | 2:
                self._parse_bone_packed()
            case 3 | 4:
                self._parse_bone_plains()
            case _:
                raise exc.McsaUnknownLinkCount(self.path, self.count.links)

    def _parse_bone_packed(self) -> None:
        # Still no export support yet
        self._skip_vertices(size=4)

    def _parse_bone_plains(self) -> None:
        # Still no export support yet
        self._skip_vertices(size=8)

    def _parse_colors(self) -> None:
        # Quite useless
        self._skip_vertices(size=4)
        return

        # Could be rgba, but not that important
        argb = self._parse_vertex_data(F.U8, Factor.U8, McsaSize.COLOR)

        for vertex, (_, r, g, b) in zip(self.vertices, argb):
            vertex.color.r = r
            vertex.color.g = g
            vertex.color.b = b

    def _parse_polygons_data(self):
        size = McsaSize.POLYGONS
        count = self.count.polygons * size
        fmt = F.U16 if count < Factor.U16 else F.U32

        data = self.f.readvalues(fmt=fmt, size=size, count=self.count.polygons)

        # In mcsa vertex indexes 0-based
        shifted = np.array(data) + 1
        reshaped = shifted.reshape(-1, size)

        return reshaped

    def _parse_polygons(self) -> None:
        abc = self._parse_polygons_data()

        for polygon, (a, b, c) in zip(self.mesh.polygons, abc):
            polygon.a = a
            polygon.b = b
            polygon.c = c

    def _parse_skeleton(self) -> None:
        # Still no export support yet
        return
