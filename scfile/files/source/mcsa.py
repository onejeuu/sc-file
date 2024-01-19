from typing import Dict

from scfile import exceptions as exc
from scfile.consts import McsaModel, Normalization, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as Format
from scfile.files.output.obj import ObjFile, ObjOutputData
from scfile.utils.mcsa.flags import Flag, McsaFlags
from scfile.utils.mcsa.scale import scaled
from scfile.utils.model import Bone, Mesh, Model, Vertex

from .base import BaseSourceFile


SUPPORTED_VERSIONS = [
    7.0,
    8.0,
    10.0
]


class McsaFile(BaseSourceFile):

    output = ObjFile
    signature = Signature.MCSA
    order = ByteOrder.LITTLE

    def to_obj(self) -> bytes:
        return self.convert()

    @property
    def data(self) -> ObjOutputData:
        return ObjOutputData(self.model)

    def parse(self) -> None:
        self.model = Model()

        self._parse_header()
        self._parse_meshes()

        if self.flags[Flag.SKELETON]:
            self._parse_skeleton()

    @property
    def scale(self):
        return self.model.scale

    def _parse_header(self) -> None:
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self):
        self.version = self.r.readbin(Format.F32)

        if self.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

    def _parse_flags(self):
        self.flags = McsaFlags(self.version)

        for index in range(self.flags.count):
            self.flags[index] = self.r.readbin(Format.BOOL)

    def _parse_scales(self):
        self.scale.position = self.r.readbin(Format.F32)

        if self.flags[Flag.UV]:
            self.scale.texture = self.r.readbin(Format.F32)

        if self.flags[Flag.NORMALS] and self.version == 10.0:
            self.scale.normals = self.r.readbin(Format.F32)

    def _parse_meshes(self) -> None:
        meshes_count = self.r.readbin(Format.U32)

        for index in range(meshes_count):
            self._parse_mesh()

    def _parse_mesh(self) -> None:
        self.mesh = Mesh()

        self._parse_name_and_material()

        self.bones: Dict[int, int] = {}

        if self.flags[Flag.SKELETON]:
            self._parse_bone_indexes()

        self._parse_counts()

        # ! unknown
        if self.flags[Flag.UV]:
            #print(self.r.tell())
            self.scale.unknown = self.r.readbin(Format.F32)
            #print(self.scale.unknown)

        # ! unknown
        if self.version == 10.0:
            for _ in range(6):
                self.r.readbin(Format.F32)

        self._parse_xyz()

        if self.flags[Flag.UV]:
            self._parse_uv()

        if self.flags[Flag.NORMALS]:
            self._parse_normals()

        # ! unknown
        self._skip_unknown()

        if self.flags[Flag.SKELETON]:
            self._parse_bones()

        if self.flags[Flag.FLAG_6]:
            self._skip_vertices()

        self._parse_polygons()

        self.model.meshes.append(self.mesh)

    @property
    def vertices(self):
        return self.mesh.vertices

    @property
    def count(self):
        return self.mesh.count

    def _parse_name_and_material(self):
        self.mesh.name = self.r.readstring()
        self.mesh.material = self.r.readstring()

    def _parse_bone_indexes(self):
        self.count.links = self.r.readbin(Format.U8)
        total_bones = self.r.readbin(Format.U8)

        for index in range(total_bones):
            self.bones[index] = self.r.readbin(Format.I8)

    def _parse_counts(self):
        self.count.vertices = self.r.mcsa_counts()
        self.count.polygons = self.r.mcsa_counts()

        self.mesh.resize_vertices(self.count.vertices)
        self.mesh.resize_polygons(self.count.polygons)

    def _parse_xyz(self) -> None:
        xyz = self.r.mcsa_xyz(self.count.vertices)
        scale = self.scale.position

        for vertex, (x, y, z, _) in zip(self.vertices, xyz):
            vertex.position.x = scaled(x, scale)
            vertex.position.y = scaled(y, scale)
            vertex.position.z = scaled(z, scale)

    def _parse_uv(self) -> None:
        uv = self.r.mcsa_uv(self.count.vertices)
        scale = self.scale.texture

        for vertex, (u, v) in zip(self.vertices, uv):
            vertex.texture.u = scaled(u, scale)
            vertex.texture.v = scaled(v, scale)

    def _parse_normals(self) -> None:
        nrm = self.r.mcsa_nrm(self.count.vertices)
        scale = self.scale.normals

        for vertex, (i, j, k, _) in zip(self.vertices, nrm):
            vertex.normals.i = scaled(i, scale, factor=Normalization.I8)
            vertex.normals.j = scaled(j, scale, factor=Normalization.I8)
            vertex.normals.k = scaled(k, scale, factor=Normalization.I8)

    def _skip_vertices(self) -> None:
        # 4 bytes per vertex
        self.r.read(self.count.vertices * 4)

    def _skip_unknown(self) -> None:
        if self.flags[Flag.FLAG_4]:
            self._skip_vertices()

        if self.flags[Flag.FLAG_5]:
            self._skip_vertices()

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
        # skip
        self.r.read(self.count.vertices * 4)
        return

        for vertex in self.vertices:
            self._parse_bone_id(vertex, 2)
            self._parse_bone_weight(vertex, 2)

    def _parse_bone_plains(self) -> None:
        # skip
        self.r.read(self.count.vertices * 8)
        return

        for vertex in self.vertices:
            self._parse_bone_id(vertex, 4)

        for vertex in self.vertices:
            self._parse_bone_weight(vertex, 4)

    def _parse_bone_id(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_id = self.r.readbin(Format.I8)
            vertex.bone.ids[index] = self.bones.get(bone_id, McsaModel.ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.r.readbin(Format.I8)
            vertex.bone.weights[index] = bone_weight / Normalization.BONE_WEIGHT

    def _parse_polygons(self) -> None:
        polygons = self.r.mcsa_polygons(self.count.polygons)

        # In obj vertex indexes starts with 1, but in mcsa with 0.
        # So we increase each one by one.
        for polygon, (v1, v2, v3) in zip(self.mesh.polygons, polygons):
            polygon.v1 = v1 + 1
            polygon.v2 = v2 + 1
            polygon.v3 = v3 + 1

    def _parse_skeleton(self) -> None:
        # Still no export support yet
        return

        bones_count = self.r.readbin(Format.I8)

        for index in range(bones_count):
            self._parse_bone(index)

    def _parse_bone(self, index: int) -> None:
        self.bone = Bone()

        self.bone.name = self.r.readstring()

        parent_id = self.r.readbin(Format.I8)
        self.bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        self._parse_bone_position()
        self._parse_bone_rotation()

        self.model.skeleton.bones.append(self.bone)

    def _parse_bone_position(self):
        self.bone.position.x = self.r.readbin(Format.F32)
        self.bone.position.y = self.r.readbin(Format.F32)
        self.bone.position.z = self.r.readbin(Format.F32)

    def _parse_bone_rotation(self):
        self.bone.rotation.x = self.r.readbin(Format.F32)
        self.bone.rotation.y = self.r.readbin(Format.F32)
        self.bone.rotation.z = self.r.readbin(Format.F32)
