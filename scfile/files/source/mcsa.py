from typing import Dict

from scfile import exceptions as exc
from scfile.consts import McsaModel, Normalization, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as Format
from scfile.files.output.obj import ObjFile, ObjOutputData
from scfile.utils.mcsa.flags import Flag, McsaFlags
from scfile.utils.model import Bone, Mesh, Model, Vertex, scaled_i16, scaled_u16

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

    def _parse_header(self) -> None:
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self):
        self.version = self.reader.readbin(Format.F32)

        if self.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

    def _parse_flags(self):
        self.flags = McsaFlags(self.version)

        for index in range(self.flags.count):
            self.flags[index] = self.reader.readbin(Format.BOOL)

    def _parse_scales(self):
        self.xyz_scale = 1.0
        self.uv_scale = 1.0

        self.xyz_scale = self.reader.readbin(Format.F32)

        if self.flags[Flag.UV]:
            self.uv_scale = self.reader.readbin(Format.F32)

        # ! unknown
        if self.flags[Flag.FLAG_3] and self.version == 10.0:
            self.unknown_scale = self.reader.readbin(Format.F32)

    def _parse_meshes(self) -> None:
        meshes_count = self.reader.readbin(Format.U32)

        for index in range(meshes_count):
            self._parse_mesh()

    def _parse_mesh(self) -> None:
        self.mesh = Mesh()

        self._parse_name_and_material()

        self.bones: Dict[int, int] = {}

        if self.flags[Flag.SKELETON]:
            self._parse_bone_indexes()

        self._parse_counts()

        self._parse_weight_scale()

        # ! unknown
        if self.version == 10.0:
            for _ in range(6):
                self.reader.readbin(Format.F32)

        self._parse_xyz()

        if self.flags[Flag.UV]:
            self._parse_uv()

        # ! unknown
        self._skip_unknown()

        if self.flags[Flag.SKELETON]:
            self._parse_bones()

        self._skip_flag_6()

        self._parse_polygons()

        self.model.meshes.append(self.mesh)

    def _parse_name_and_material(self):
        # I'm still not sure?
        match self.version:
            case 7.0:
                self.mesh.name = self.reader.readstring()
                self.mesh.material = self.reader.readstring()
            case 8.0 | 10.0:
                self.mesh.material = self.reader.readstring()
                self.mesh.name = self.reader.readstring()

    def _parse_bone_indexes(self):
        self.mesh.link_count = self.reader.readbin(Format.U8)
        total_bones = self.reader.readbin(Format.U8)

        for index in range(total_bones):
            self.bones[index] = self.reader.readbin(Format.I8)

    def _parse_counts(self):
        self.vertices_count = self.reader.mcsa_counts()
        self.polygons_count = self.reader.mcsa_counts()

        self.mesh.resize_vertices(self.vertices_count)
        self.mesh.resize_polygons(self.polygons_count)

    def _parse_weight_scale(self):
        self.weight_scale = 1.0

        # ! unknown
        if self.flags[Flag.UV]:
            self.weight_scale = self.reader.readbin(Format.F32)

    def _parse_xyz(self) -> None:
        vertices = self.reader.mcsa_xyz(self.vertices_count)

        for vertex, (x, y, z, w) in zip(self.mesh.vertices, vertices):
            vertex.position.x = scaled_i16(x, self.xyz_scale)
            vertex.position.y = scaled_i16(y, self.xyz_scale)
            vertex.position.z = scaled_i16(z, self.xyz_scale)
            vertex.position.w = scaled_u16(w, self.weight_scale)

    def _parse_uv(self) -> None:
        vertices = self.reader.mcsa_uv(self.vertices_count)

        for vertex, (u, v) in zip(self.mesh.vertices, vertices):
            vertex.texture.u = scaled_i16(u, self.uv_scale)
            vertex.texture.v = scaled_i16(v, self.uv_scale)

    def _skip_vertices(self) -> None:
        # 4 bytes per vertex
        self.reader.read(self.vertices_count * 4)

    def _skip_unknown(self) -> None:
        if self.flags[Flag.FLAG_3]:
            self._skip_vertices()

        if self.flags[Flag.FLAG_4]:
            self._skip_vertices()

        if self.flags[Flag.FLAG_5]:
            self._skip_vertices()

    def _parse_bones(self) -> None:
        match self.mesh.link_count:
            case 0:
                pass
            case 1 | 2:
                self._parse_bone_packed()
            case 3 | 4:
                self._parse_bone_plains()
            case _:
                raise exc.McsaUnknownLinkCount(self.path, self.mesh.link_count)

    def _parse_bone_packed(self) -> None:
        for vertex in self.mesh.vertices:
            self._parse_bone_id(vertex, 2)
            self._parse_bone_weight(vertex, 2)

    def _parse_bone_plains(self) -> None:
        for vertex in self.mesh.vertices:
            self._parse_bone_id(vertex, 4)

        for vertex in self.mesh.vertices:
            self._parse_bone_weight(vertex, 4)

    def _parse_bone_id(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_id = self.reader.readbin(Format.I8)
            vertex.bone.ids[index] = self.bones.get(bone_id, McsaModel.ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.reader.readbin(Format.I8)
            vertex.bone.weights[index] = bone_weight / Normalization.BONE_WEIGHT

    def _skip_flag_6(self):
        if self.flags[Flag.FLAG_6]:
            self._skip_vertices()

    def _parse_polygons(self) -> None:
        polygons = self.reader.mcsa_polygons(self.polygons_count)

        # In obj vertex indexes starts with 1, but in mcsa with 0.
        # So we increase each one by one.
        for polygon, (v1, v2, v3) in zip(self.mesh.polygons, polygons):
            polygon.v1 = v1 + 1
            polygon.v2 = v2 + 1
            polygon.v3 = v3 + 1

    def _parse_skeleton(self) -> None:
        # Still no export support yet
        return

        bones_count = self.reader.readbin(Format.I8)

        for index in range(bones_count):
            self._parse_bone(index)

    def _parse_bone(self, index: int) -> None:
        self.bone = Bone()

        self.bone.name = self.reader.readstring()

        parent_id = self.reader.readbin(Format.I8)
        self.bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        self._parse_bone_position()
        self._parse_bone_rotation()

        self.model.skeleton.bones.append(self.bone)

    def _parse_bone_position(self):
        self.bone.position.x = self.reader.readbin(Format.F32)
        self.bone.position.y = self.reader.readbin(Format.F32)
        self.bone.position.z = self.reader.readbin(Format.F32)

    def _parse_bone_rotation(self):
        self.bone.rotation.x = self.reader.readbin(Format.F32)
        self.bone.rotation.y = self.reader.readbin(Format.F32)
        self.bone.rotation.z = self.reader.readbin(Format.F32)
