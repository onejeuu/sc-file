from typing import Dict

from scfile import exceptions as exc
from scfile.consts import MODEL_ROOT_BONE_ID, Normalization, Signature
from scfile.files import ObjFile
from scfile.reader import ByteOrder
from scfile.utils.mcsa_flags import Flag, McsaFlags
from scfile.utils.model import Bone, Mesh, Model, Vertex, scaled

from .base import BaseSourceFile


SUPPORTED_VERSIONS = [
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
        self.model = Model()

        self._parse_header()
        self._parse_meshes()
        self._parse_skeleton()

    def _parse_header(self) -> None:
        # Read mcsa format version
        self.version = self.reader.f32()

        if self.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

        # Read model flags
        self.flags = McsaFlags(self.version)

        for index in range(self.flags.count):
            self.flags[index] = self.reader.i8()

        if self.flags.unsupported:
            raise exc.McsaUnsupportedFlags(self.path, self.flags)

        # Read scales
        self.xyz_scale = self.reader.f32()
        self.uv_scale = 1.0

        if self.flags[Flag.UV]:
            self.uv_scale = self.reader.f32()

    def _parse_meshes(self) -> None:
        meshes_count = self.reader.u32()

        for index in range(meshes_count):
            self._parse_mesh(index)

    def _parse_mesh(self, index: int) -> None:
        self.mesh = Mesh()

        self.mesh.name = self.reader.mcsastring()
        self.mesh.material = self.reader.mcsastring()

        self._parse_bone_indexes()

        self.mesh.resize_vertices(self.reader.u32())
        self.mesh.resize_polygons(self.reader.u32())

        if self.flags[Flag.VERTEX_WEIGHT]:
            self.weight_scale = self.reader.f32()

        self._parse_xyz()
        self._parse_uv()

        # ! unknown
        self._skip_unknown()
        self._skip_flag_10()

        self._parse_bones()
        self._parse_polygons()
        self._parse_normals()

        self.model.meshes[index] = self.mesh

    def _parse_bone_indexes(self):
        link_count = 0
        self.bones: Dict[int, int] = {}

        if self.flags[Flag.SKELETON]:
            link_count = self.reader.u8()
            total_bones = self.reader.u8()

            for index in range(total_bones):
                self.bones[index] = self.reader.i8()

        self.mesh.link_count = link_count

    def _parse_xyz(self) -> None:
        for vertex in self.mesh.vertices:
            vertex.position.x = scaled(self.xyz_scale, self.reader.i16())
            vertex.position.y = scaled(self.xyz_scale, self.reader.i16())
            vertex.position.z = scaled(self.xyz_scale, self.reader.i16())

            if self.flags[Flag.VERTEX_WEIGHT]:
                vertex.weight = scaled(self.weight_scale, self.reader.u16())

    def _parse_uv(self) -> None:
        if self.flags[Flag.UV]:
            for vertex in self.mesh.vertices:
                vertex.texture.u = scaled(self.uv_scale, self.reader.i16())
                vertex.texture.v = scaled(self.uv_scale, self.reader.i16())

    def _parse_normals(self) -> None:
        if self.flags[Flag.NORMALS]:
            self.reader.read(len(self.mesh.polygons) * 6)

    def _skip_flag_10(self):
        if self.flags[Flag.FLAG_10]:
            self.reader.read(42)

    def _skip_vertices(self) -> None:
        # 4 bytes per vertex
        self.reader.read(len(self.mesh.vertices) * 4)

    def _skip_unknown(self) -> None:
        if self.flags[Flag.NORMALS]:
            for vertex in self.mesh.vertices:
                vertex.normals.x = scaled(1.0, self.reader.i16())
                vertex.normals.y = scaled(1.0, self.reader.i16())
                vertex.normals.z = scaled(1.0, self.reader.i16())
                self.reader.read(2)

        if self.flags[Flag.FLAG_5]:
            self._skip_vertices()

    def _parse_bones(self) -> None:
        if self.flags[Flag.SKELETON]:
            match self.mesh.link_count:
                case 0:
                    pass
                case 1 | 2:
                    self._parse_bone_packed()
                case 3 | 4:
                    self._parse_bone_plains()
                case _:
                    raise exc.McsaUnsupportedLinkCount(self.path, self.mesh.link_count)

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
            vertex.bone.ids[index] = self.bones.get(bone_id, MODEL_ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.reader.i8()
            vertex.bone.weights[index] = bone_weight / Normalization.BONE_WEIGHT

    def _parse_polygons(self) -> None:
        for polygon in self.mesh.polygons:
            polygon.vertex1 = self._read_vertex()
            polygon.vertex2 = self._read_vertex()
            polygon.vertex3 = self._read_vertex()

    def _read_vertex(self) -> int:
        if len(self.mesh.vertices) >= Normalization.VERTEX_LIMIT:
            return self.reader.u32() + 1
        return self.reader.u16() + 1

    def _parse_skeleton(self) -> None:
        if self.flags[Flag.SKELETON]:
            bones_count = self.reader.i8()

            for index in range(bones_count):
                self._parse_bone(index)

    def _parse_bone(self, index: int) -> None:
        bone = Bone()

        bone.name = self.reader.mcsastring()

        parent_id = self.reader.i8()
        bone.parent_id = parent_id if parent_id != index else MODEL_ROOT_BONE_ID

        bone.position.x = self.reader.f32()
        bone.position.y = self.reader.f32()
        bone.position.z = self.reader.f32()

        bone.rotation.x = self.reader.f32()
        bone.rotation.y = self.reader.f32()
        bone.rotation.z = self.reader.f32()

        self.model.skeleton.bones[index] = bone
