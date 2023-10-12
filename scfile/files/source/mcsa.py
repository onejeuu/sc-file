from typing import Dict

from scfile import exceptions as exc
from scfile.consts import ROOT_BONE_ID, FLAGS_COUNT_OFFSET, Normalization, Signature
from scfile.files import ObjFile
from scfile.utils.model import Bone, Mesh, Model, Vertex, scaled
from scfile.utils.reader import ByteOrder
from scfile.utils.mcsa_flags import Flags, McsaFlags

from .base import BaseSourceFile


_SUPPORTED_VERSIONS = [
    7.0,
    8.0
]


class McsaFile(BaseSourceFile):

    signature = Signature.MCSA
    order = ByteOrder.LITTLE

    def to_obj(self) -> bytes:
        return self.convert()

    def _output(self) -> ObjFile:
        return ObjFile(
            self.buffer,
            self.filename,
            self.model
        )

    def _parse(self) -> None:
        # creating model dataclass
        self.model = Model()

        # parsing file data
        self._parse_header()
        self._parse_meshes()
        self._parse_skeleton()

    def _parse_header(self) -> None:
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self) -> None:
        self.version = self.reader.f32()
        self._check_version()

    @property
    def _flags_count(self) -> int:
        return int(self.version - FLAGS_COUNT_OFFSET)

    def _parse_flags(self) -> None:
        self.flags = McsaFlags()

        for index in range(self._flags_count):
            self.flags[index] = self.reader.i8()

        self._check_flags()

    def _parse_scales(self) -> None:
        self.xyz_scale = self.reader.f32()
        self.uv_scale = 1.0

        if self.flags[Flags.UV]:
            self.uv_scale = self.reader.f32()

    def _parse_meshes(self) -> None:
        meshes_count = self.reader.u32()

        for index in range(meshes_count):
            self._parse_mesh(index)

    def _parse_mesh(self, index: int) -> None:
        # creating mesh dataclass
        self.mesh = Mesh()

        self.mesh.name = self.reader.mcsastring()
        self.mesh.material = self.reader.mcsastring()

        self._parse_bone_indexes()
        self._parse_counts()

        # ! unknown
        self._skip_flag_3()

        # parsing model geometric vertices
        self._parse_xyz()

        # parsing model texture coordinates
        self._parse_uv()

        # ! unknown
        self._skip_unknown()

        self._parse_bones()
        self._parse_polygons()

        self.model.meshes[index] = self.mesh

    def _parse_bone_indexes(self):
        link_count = 0
        self.bones: Dict[int, int] = {}

        if self.flags[Flags.SKELETON]:
            link_count = self.reader.i8()
            total_bones = self.reader.i8()

            for index in range(total_bones):
                self.bones[index] = self.reader.i8()

        self.mesh.link_count = link_count

    def _parse_counts(self):
        # fill mesh vertices list to empty vertices
        vertices_count = self.reader.u32()
        self.mesh.resize_vertices(vertices_count)

        # fill mesh polygons list to empty polygons
        polygons_count = self.reader.u32()
        self.mesh.resize_polygons(polygons_count)

    def _skip_flag_3(self):
        if self.flags[Flags.FLAG_3]:
            self.reader.f32()

    def _parse_xyz(self) -> None:
        for vertex in self.mesh.vertices:
            vertex.position.x = scaled(self.xyz_scale, self.reader.i16())
            vertex.position.y = scaled(self.xyz_scale, self.reader.i16())
            vertex.position.z = scaled(self.xyz_scale, self.reader.i16())
            self.reader.i16() # delimiter

    def _parse_uv(self) -> None:
        if self.flags[Flags.UV]:
            for vertex in self.mesh.vertices:
                vertex.texture.u = scaled(self.uv_scale, self.reader.i16())
                vertex.texture.v = scaled(self.uv_scale, self.reader.i16())

    def _skip(self) -> None:
        for _ in self.mesh.vertices:
            self.reader.i16()
            self.reader.i16()

    def _skip_unknown(self) -> None:
        if self.flags[Flags.FLAG_3]:
            self._skip()

        if self.flags[Flags.FLAG_4]:
            self._skip()

    def _parse_bones(self) -> None:
        match self.mesh.link_count:
            case 0: pass
            case 1 | 2: self._parse_bone_packed()
            case 3 | 4: self._parse_bone_plains()
            case _:
                raise exc.McsaUnsupportedLinkCount(f"Unsupported mcsa link count: {self.mesh.link_count}")

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
            bone_id = self.reader.i8()
            vertex.bone.ids[index] = self.bones.get(bone_id, ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.reader.i8()
            vertex.bone.weights[index] = bone_weight / Normalization.BONE_WEIGHT

    def _parse_polygons(self) -> None:
        for polygon in self.mesh.polygons:
            polygon.vertex1 = self._read_vertex_id()
            polygon.vertex2 = self._read_vertex_id()
            polygon.vertex3 = self._read_vertex_id()

    def _read_vertex_id(self) -> int:
        # + 1 for .obj standart
        if len(self.mesh.vertices) >= Normalization.VERTEX_LIMIT:
            return self.reader.u32() + 1
        return self.reader.u16() + 1

    def _parse_skeleton(self) -> None:
        if self.flags[Flags.SKELETON]:
            bones_count = self.reader.i8()

            for index in range(bones_count):
                self._parse_bone(index)

    def _parse_bone(self, index: int) -> None:
        bone = Bone()

        bone.name = self.reader.mcsastring()
        parent_id = self.reader.i8()
        bone.parent_id = parent_id if parent_id != index else ROOT_BONE_ID

        self._parse_bone_position(bone)
        self._parse_bone_rotation(bone)

        self.model.skeleton.bones[index] = bone

    def _parse_bone_position(self, bone: Bone):
        bone.position.x = self.reader.f32()
        bone.position.y = self.reader.f32()
        bone.position.z = self.reader.f32()

    def _parse_bone_rotation(self, bone: Bone):
        bone.rotation.x = self.reader.f32()
        bone.rotation.y = self.reader.f32()
        bone.rotation.z = self.reader.f32()

    def _check_version(self):
        if self.version not in _SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(f"Unsupported mcsa version: {self.version}")

    def _check_flags(self):
        if self.flags.unsupported:
            raise exc.McsaUnsupportedFlags(f"Unsupported mcsa flags: {self.flags}")
