from scfile import exceptions as exc
from scfile.consts import McsaModel, Factor, Signature
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
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
        """Shortcut for model scales."""
        return self.model.scale

    def _parse_header(self) -> None:
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self):
        self.version = self.r.readbin(F.F32)

        if self.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

    def _parse_flags(self):
        self.flags = McsaFlags(self.version)

        for index in range(self.flags.count):
            self.flags[index] = self.r.readbin(F.BOOL)

    def _parse_scales(self):
        self.scale.position = self.r.readbin(F.F32)

        if self.flags[Flag.UV]:
            self.scale.texture = self.r.readbin(F.F32)

        # ! unconfirmed (version)
        if self.flags[Flag.NORMALS] and self.version == 10.0:
            self.scale.normals = self.r.readbin(F.F32)

    def _parse_meshes(self) -> None:
        meshes_count = self.r.readbin(F.U32)

        for index in range(meshes_count):
            self._parse_mesh()

    def _parse_mesh(self) -> None:
        self.mesh = Mesh()

        self._parse_name_and_material()

        if self.flags[Flag.SKELETON]:
            self._parse_bone_indexes()

        self._parse_counts()

        # ! unknown
        # ! unconfirmed (flag)
        if self.flags[Flag.UV]:
            self.scale.bones = self.r.readbin(F.F32)

        # ! unknown
        # flag 4, 5 (xyz, xyz) ?
        if self.version == 10.0:
            for _ in range(6):
                self.r.readbin(F.F32)

        self._parse_position()

        if self.flags[Flag.UV]:
            self._parse_texture()

        if self.flags[Flag.NORMALS]:
            self._parse_normals()

        # ! unknown
        self._skip_unknown()

        if self.flags[Flag.SKELETON]:
            self._parse_bones()

        # ! unknown
        # bone weights? or smth else with skeleton
        if self.flags[Flag.FLAG_6]:
            self._skip_vertices()

        self._parse_polygons()

        self.model.meshes.append(self.mesh)

    @property
    def vertices(self):
        """Shortcut for current mesh vertices."""
        return self.mesh.vertices

    @property
    def count(self):
        """Shortcut for current mesh counts."""
        return self.mesh.count

    def _parse_name_and_material(self):
        self.mesh.name = self.r.readstring()
        self.mesh.material = self.r.readstring()

    def _parse_bone_indexes(self):
        self.count.links = self.r.readbin(F.U8)
        self.count.bones = self.r.readbin(F.U8)

        for index in range(self.count.bones):
            self.mesh.bones[index] = self.r.readbin(F.I8)

    def _parse_counts(self):
        self.count.vertices = self.r.mcsa_counts()
        self.count.polygons = self.r.mcsa_counts()
        self.mesh.resize()

    def _parse_position(self) -> None:
        xyz = self.r.mcsa_xyz(self.count.vertices)
        self.mesh.load_position(xyz, self.scale.position)

    def _parse_texture(self) -> None:
        uv = self.r.mcsa_uv(self.count.vertices)
        self.mesh.load_texture(uv, self.scale.texture)

    def _parse_normals(self) -> None:
        nrm = self.r.mcsa_nrm(self.count.vertices)
        self.mesh.load_normals(nrm, self.scale.normals)

    def _skip_vertices(self, size: int = 4) -> None:
        # size: bytes per vertex
        self.r.read(self.count.vertices * size)

    def _skip_unknown(self) -> None:
        # ! unconfirmed change
        if self.flags[Flag.TANGENTS]:
            self._skip_vertices()

        # ! unconfirmed change
        if self.flags[Flag.BITANGENTS]:
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
        # ! slow parsing, useless (now), so skip
        self._skip_vertices(size=4)
        return

        for vertex in self.vertices:
            self._parse_bone_id(vertex, 2)
            self._parse_bone_weight(vertex, 2)

    def _parse_bone_plains(self) -> None:
        # ! slow parsing, useless (now), so skip
        self._skip_vertices(size=8)
        return

        for vertex in self.vertices:
            self._parse_bone_id(vertex, 4)

        for vertex in self.vertices:
            self._parse_bone_weight(vertex, 4)

    def _parse_bone_id(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_id = self.r.readbin(F.I8)
            vertex.bone.ids[index] = self.mesh.bones.get(bone_id, McsaModel.ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.r.readbin(F.I8)
            vertex.bone.weights[index] = scaled(bone_weight, self.scale.bones, factor=Factor.BONE_WEIGHT)

    def _parse_polygons(self) -> None:
        polygons = self.r.mcsa_polygons(self.count.polygons)
        self.mesh.load_polygons(polygons)

    def _parse_skeleton(self) -> None:
        # Still no export support yet
        return

        bones_count = self.r.readbin(F.I8)

        for index in range(bones_count):
            self._parse_bone(index)

    def _parse_bone(self, index: int) -> None:
        self.bone = Bone()

        self.bone.name = self.r.readstring()

        parent_id = self.r.readbin(F.I8)
        self.bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        self._parse_bone_position()
        self._parse_bone_rotation()

        self.model.skeleton.bones.append(self.bone)

    def _parse_bone_position(self):
        self.bone.position.x = self.r.readbin(F.F32)
        self.bone.position.y = self.r.readbin(F.F32)
        self.bone.position.z = self.r.readbin(F.F32)

    def _parse_bone_rotation(self):
        self.bone.rotation.x = self.r.readbin(F.F32)
        self.bone.rotation.y = self.r.readbin(F.F32)
        self.bone.rotation.z = self.r.readbin(F.F32)
