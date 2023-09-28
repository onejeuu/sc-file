from typing import NamedTuple, Dict

from scfile import exceptions as exc
from scfile.base import BaseInputFile
from scfile.consts import Signature, Normalization, ROOT_BONE_ID
from scfile.model import Bone, Mesh, Model, Vertex, scaled
from scfile.obj import ObjFile
from scfile.reader import ByteOrder


class Flag(NamedTuple):
    SKELETON = 0
    UV = 1
    FLAG_3 = 2
    FLAG_4 = 3
    FLAG_5 = 4


class McsaFile(BaseInputFile):
    @property
    def signature(self) -> int:
        return Signature.MCSA

    def to_obj(self) -> bytes:
        self._convert()

        ObjFile(
            self.buffer,
            self.model,
            self.filename
        ).create()

        return self.output

    def _convert(self) -> bytes:
        # change default byte order
        # to avoid specifying it every time
        self.reader.order = ByteOrder.LITTLE

        # creating model dataclass
        self.model = Model()

        # parsing mcsa header
        self._parse_header()

        # parsing meshes
        for i in range(self.meshes_count):
            self.model.meshes[i] = self._parse_mesh()

        # parsing skeleton (if exists)
        if self._SKELETON_PRESENT:
            self._parse_skeleton()

        return self.output

    def _parse_header(self) -> None:
        version = self.reader.float()

        flags_count = 0

        match version:
            case 7.0 | 8.0: flags_count = int(version - 3.0)
            case _: raise exc.UnknownVersion()

        self.flags: Dict[int, int] = self._create_flags()

        for i in range(flags_count):
            self.flags[i] = self.reader.byte()

        if self._flags_unsupported:
            raise exc.UnsupportedFlags()

        self.xyz_scale = self.reader.float()
        self.uv_scale = 0.0

        if self._UV_PRESENT:
            self.uv_scale = self.reader.float()

        self.meshes_count = self.reader.udword()

    def _parse_mesh(self) -> Mesh:
        # creating mesh dataclass
        self.mesh = Mesh()

        # ! refactor this
        try:
            self.mesh.name = self.reader.mcsastring()
            self.mesh.material = self.reader.mcsastring()

        except ValueError:
            raise exc.McsaFileError(
                "Cannot read string, maybe .mcsa file structure was updated"
            )

        # parsing bone indexes
        self._parse_bone_indexes()

        # fill mesh vertices list to empty vertices
        vertices_count = self.reader.udword()
        self.mesh.resize_vertices(vertices_count)

        # fill mesh polygons list to empty polygons
        polygons_count = self.reader.udword()
        self.mesh.resize_polygons(polygons_count)

        # ! unknown
        if self.flags[Flag.FLAG_3] != 0:
            self.reader.float()

        # parsing model geometric vertices
        self._parse_xyz()

        # parsing model texture coordinates
        self._parse_uv()

        # ! unknown
        self._skip_unknown()

        self._parse_bones()
        self._parse_polygons()

        return self.mesh

    def _parse_bone_indexes(self):
        self.bones_link_count = 0
        self.bones: Dict[int, int] = {}

        if self._SKELETON_PRESENT:
            self.bones_link_count = self.reader.byte()
            total_bones = self.reader.byte()

            for index in range(total_bones):
                self.bones[index] = self.reader.byte()

    def _parse_xyz(self) -> None:
        for vertex in self.mesh.vertices:
            vertex.position.x = scaled(self.xyz_scale, self.reader.sword())
            vertex.position.y = scaled(self.xyz_scale, self.reader.sword())
            vertex.position.z = scaled(self.xyz_scale, self.reader.sword())
            self.reader.uword() # delimiter

    def _parse_uv(self) -> None:
        if self._UV_PRESENT:
            for vertex in self.mesh.vertices:
                vertex.texture.u = scaled(self.uv_scale, self.reader.sword())
                vertex.texture.v = scaled(self.uv_scale, self.reader.sword())

    def _skip(self) -> None:
        for _ in self.mesh.vertices:
            self.reader.sword()
            self.reader.sword()

    def _skip_unknown(self) -> None:
        if self.flags[Flag.FLAG_3] != 0:
            self._skip()

        if self.flags[Flag.FLAG_4] != 0:
            self._skip()

    def _parse_bones(self) -> None:
        match self.bones_link_count:
            case 1 | 2: self._parse_bone_packed()
            case 3 | 4: self._parse_bone_plains()
            case _: raise exc.UnsupportedLinkCount()

    def _parse_bone_packed(self) -> None:
        for vertex in self.mesh.vertices:
            vertex.bone_count = self.bones_link_count
            self._parse_bone_id(vertex, 2)
            self._parse_bone_weight(vertex, 2)

    def _parse_bone_plains(self) -> None:
        for vertex in self.mesh.vertices:
            vertex.bone_count = self.bones_link_count
            self._parse_bone_id(vertex, 4)

        for vertex in self.mesh.vertices:
            self._parse_bone_weight(vertex, 4)

    def _parse_bone_id(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_id = self.reader.byte()
            vertex.bone_ids[index] = self.bones.get(bone_id, ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.reader.byte()
            vertex.bone_weights[index] = bone_weight / Normalization.BONE_WEIGHT

    def _parse_polygons(self) -> None:
        for polygon in self.mesh.polygons:
            polygon.vertex1 = self._read_vertex_id()
            polygon.vertex2 = self._read_vertex_id()
            polygon.vertex3 = self._read_vertex_id()

    def _read_vertex_id(self) -> int:
        # + 1 for .obj standart
        if len(self.mesh.vertices) >= Normalization.VERTEX_LIMIT:
            return self.reader.udword() + 1
        return self.reader.uword() + 1

    def _parse_skeleton(self) -> None:
        bones_count = self.reader.byte()

        for index in range(bones_count):
            self._parse_skeleton_bone(index)

    def _parse_skeleton_bone(self, index: int) -> None:
        bone = Bone()

        try:
            bone.name = self.reader.mcsastring()

        except ValueError:
            raise exc.McsaFileError(
                "Cannot read string, maybe .mcsa file structure was updated"
            )

        parent_id = self.reader.byte()
        bone.parent_id = parent_id if parent_id != index else ROOT_BONE_ID

        self._parse_bone_position(bone)
        self._parse_bone_rotation(bone)

        self.model.skeleton.bones[index] = bone

    def _parse_bone_position(self, bone: Bone):
        bone.position.x = self.reader.float()
        bone.position.y = self.reader.float()
        bone.position.z = self.reader.float()

    def _parse_bone_rotation(self, bone: Bone):
        bone.rotation.x = self.reader.float()
        bone.rotation.y = self.reader.float()
        bone.rotation.z = self.reader.float()

    def _create_flags(self):
        # bruh
        return {i: 0 for i in range(6)}

    @property
    def _SKELETON_PRESENT(self):
        return self.flags[Flag.SKELETON] != 0

    @property
    def _UV_PRESENT(self):
        return self.flags[Flag.UV] != 0

    @property
    def _flags_unsupported(self):
        return  (self.flags[Flag.FLAG_5] == 1) or \
                (self.flags[Flag.UV] == 0 and self.flags[Flag.FLAG_3] == 1) or \
                (self.flags[Flag.UV] == 1 and self.flags[Flag.FLAG_3] == 0)
