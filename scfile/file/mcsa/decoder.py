from more_itertools import chunked

from scfile import exceptions as exc
from scfile.consts import Factor, McsaSize, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.file.data import ModelData
from scfile.file.decoder import FileDecoder
from scfile.file.obj.encoder import ObjEncoder
from scfile.io.mcsa import McsaFileIO
from scfile.utils.model import Mesh, Model

from .flags import Flag, McsaFlags
from .scale import scaled
from .versions import SUPPORTED_VERSIONS


class McsaDecoder(FileDecoder[McsaFileIO, ModelData]):
    def to_obj(self):
        return self.convert(ObjEncoder)

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
        # TODO: Fix normals with flag 4 & 5

        return ModelData(
            self.model,
            self.flags[Flag.TEXTURE],
            self.flags[Flag.NORMALS],
        )

    def parse(self):
        self.model = Model()

        self._parse_header()
        self._parse_meshes()

    @property
    def m(self):
        return self.model

    def _parse_header(self):
        # Version
        version = self.f.readb(F.F32)
        self.version = SUPPORTED_VERSIONS.find(version)

        if not self.version:
            raise exc.McsaUnsupportedVersion(self.path, version)

        # Flags
        self.flags = McsaFlags()

        for index in range(self.version.flags):
            self.flags[index] = self.f.readb(F.BOOL)

        # Scales
        self.m.scale.position = self.f.readb(F.F32)

        if self.flags[Flag.TEXTURE]:
            self.m.scale.texture = self.f.readb(F.F32)

        # ! unconfirmed (version)
        if self.flags[Flag.NORMALS] and self.version == 10.0:
            self.m.scale.normals = self.f.readb(F.F32)

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

        # ! unknown
        # ! unconfirmed (flag) ???
        if self.flags[Flag.TEXTURE]:
            self.m.scale.weight = self.f.readb(F.F32)

        # ! unknown
        # flag 4, 5 (xyz, xyz) ?
        if self.version == 10.0:
            for _ in range(6):
                self.f.readb(F.F32)

        # Geometric vertices
        self._parse_position()

        # Texture vertices
        if self.flags[Flag.TEXTURE]:
            self._parse_texture()

        # Vertex normals
        if self.flags[Flag.NORMALS]:
            self._parse_normals()

        # ! unknown
        self._skip_unknown()

        # Skeleton bones
        if self.flags[Flag.SKELETON]:
            self._parse_bones()

        # ! unknown
        # bone weights? or smth else with skeleton
        if self.flags[Flag.FLAG_6]:
            self._skip_vertices()

        # Polygon faces
        self._parse_polygons()

        self.model.meshes.append(self.mesh)

    @property
    def count(self):
        return self.mesh.count

    def _parse_bone_indexes(self):
        self.count.links = self.f.readb(F.U8)
        self.count.bones = self.f.readb(F.U8)

        for index in range(self.count.bones):
            self.mesh.bones[index] = self.f.readb(F.I8)

    @property
    def vertices(self):
        return self.mesh.vertices

    @property
    def scale(self):
        return self.model.scale

    def _parse_position(self) -> None:
        size = McsaSize.POSITION
        xyz = self.f.readvalues(fmt=F.I16, size=size, count=self.count.vertices)

        scale = self.scale.position
        factor = Factor.I16

        for vertex, (x, y, z, _) in zip(self.vertices, chunked(xyz, size)):
            vertex.position.x = scaled(x, scale, factor)
            vertex.position.y = scaled(y, scale, factor)
            vertex.position.z = scaled(z, scale, factor)

    def _parse_texture(self) -> None:
        size = McsaSize.TEXTURE
        uv = self.f.readvalues(fmt=F.I16, size=size, count=self.count.vertices)

        scale = self.scale.texture
        factor = Factor.I16

        for vertex, (u, v) in zip(self.vertices, chunked(uv, size)):
            vertex.texture.u = scaled(u, scale, factor)
            vertex.texture.u = scaled(v, scale, factor)

    def _parse_normals(self) -> None:
        size = McsaSize.NORMALS
        xyz = self.f.readvalues(fmt=F.I8, size=size, count=self.count.vertices)

        scale = self.scale.normals
        factor = Factor.I8

        for vertex, (x, y, z, _) in zip(self.vertices, chunked(xyz, size)):
            vertex.normals.x = scaled(x, scale, factor)
            vertex.normals.y = scaled(y, scale, factor)
            vertex.normals.z = scaled(z, scale, factor)

    def _skip_vertices(self, size: int = 4) -> None:
        self.f.read(self.count.vertices * size)

    def _skip_unknown(self) -> None:
        # ! unconfirmed change
        if self.flags[Flag.TANGENTS]:
            self._skip_vertices(size=4)

        # ! unconfirmed change
        if self.flags[Flag.BITANGENTS]:
            self._skip_vertices(size=4)

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

    def _parse_polygons(self) -> None:
        count = self.count.polygons * McsaSize.POLYGONS
        fmt = F.U16 if count < Factor.U16 else F.U32
        size = McsaSize.POLYGONS

        polygons = self.f.readvalues(fmt=fmt, size=size, count=self.count.polygons)

        for polygon, (v1, v2, v3) in zip(self.mesh.polygons, chunked(polygons, size)):
            # In obj vertex indexes starts with 1, but in mcsa with 0.
            # So we increase each one by one.
            polygon.v1 = v1 + 1
            polygon.v2 = v2 + 1
            polygon.v3 = v3 + 1

    def _parse_skeleton(self) -> None:
        # Still no export support yet
        return
