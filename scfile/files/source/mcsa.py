from scfile import exceptions as exc
from scfile.consts import McsaModel, Normalization, Signature
from scfile.files.output.obj import ObjFile, ObjOutputData
from scfile.reader import ByteOrder
from scfile.utils.mcsa_flags import Flag, McsaFlags
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
        self.version = self.reader.f32()

        #print()
        #print("FILE:", self.filename)
        #print("version:", self.version)

        if self.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.version)

    def _parse_flags(self):
        self.flags = McsaFlags(self.version)

        for index in range(self.flags.count):
            self.flags[index] = self.reader.i8()

        #print("flags:", self.flags)

    def _parse_scales(self):
        self.xyz_scale = 1.0
        self.uv_scale = 1.0

        self.xyz_scale = self.reader.f32()

        if self.flags[Flag.UV]:
            self.uv_scale = self.reader.f32()

        # ! unknown
        if self.flags[Flag.FLAG_3] and self.version == 10.0:
            self.unknown_scale = self.reader.f32()
            #print("unknown scale:", self.unknown_scale)

        #print("xyz scale:", self.xyz_scale)
        #print("uv scale:", self.uv_scale)

    def _parse_meshes(self) -> None:
        meshes_count = self.reader.u32()

        for index in range(meshes_count):
            self._parse_mesh()

    def _parse_mesh(self) -> None:
        self.mesh = Mesh()

        #print()
        #print("mesh:", self.reader.tell())

        self._parse_name_and_material()

        #print(self.mesh.name[:15])

        #print("bone indexes:", self.reader.tell())
        self.bones: dict[int, int] = {}

        if self.flags[Flag.SKELETON]:
            self._parse_bone_indexes()

        #print("counts:", self.reader.tell())
        self._parse_counts()

        #print("weight_scale:", self.reader.tell())
        self._parse_weight_scale()

        # ! unknown
        #print("unknown v10:", self.reader.tell())
        if self.version == 10.0:
            # ??????
            for _ in range(6):
                self.reader.f32()

        #print("xyz:", self.reader.tell())
        self._parse_xyz()

        #print("uv:", self.reader.tell())
        if self.flags[Flag.UV]:
            self._parse_uv()

        # ! unknown
        #print("unknown:", self.reader.tell())
        self._skip_unknown()

        #print("bones:", self.reader.tell())
        if self.flags[Flag.SKELETON]:
            self._parse_bones()

        self._skip_flag_6()

        #print("polygons:", self.reader.tell())
        self._parse_polygons()

        self.model.meshes.append(self.mesh)

    def _parse_name_and_material(self):
        # v7 = name, material
        # v8 = name, material
        match self.version:
            case 7.0:
                self.mesh.name = self.reader.string_mcsa()
                self.mesh.material = self.reader.string_mcsa()
            case 8.0 | 10.0:
                self.mesh.material = self.reader.string_mcsa()
                self.mesh.name = self.reader.string_mcsa()

    def _parse_bone_indexes(self):
        self.mesh.link_count = self.reader.u8()
        total_bones = self.reader.u8()

        for index in range(total_bones):
            self.bones[index] = self.reader.i8()

    def _parse_counts(self):
        self.vertices_count = self.reader.mcsa_counts()
        self.polygons_count = self.reader.mcsa_counts()

        #print(f"v {self.vertices_count}, p {self.polygons_count}")

        self.mesh.resize_vertices(self.vertices_count)
        self.mesh.resize_polygons(self.polygons_count)

    def _parse_weight_scale(self):
        self.weight_scale = 1.0

        # ! unknown
        if self.flags[Flag.UV]:
            self.weight_scale = self.reader.f32()

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
            bone_id = self.reader.i8()
            vertex.bone.ids[index] = self.bones.get(bone_id, McsaModel.ROOT_BONE_ID)

    def _parse_bone_weight(self, vertex: Vertex, size: int) -> None:
        for index in range(size):
            bone_weight = self.reader.i8()
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

        bones_count = self.reader.i8()

        for index in range(bones_count):
            self._parse_bone(index)

    def _parse_bone(self, index: int) -> None:
        self.bone = Bone()

        self.bone.name = self.reader.string_mcsa()

        parent_id = self.reader.i8()
        self.bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        self._parse_bone_position()
        self._parse_bone_rotation()

        self.model.skeleton.bones.append(self.bone)

    def _parse_bone_position(self):
        self.bone.position.x = self.reader.f32()
        self.bone.position.y = self.reader.f32()
        self.bone.position.z = self.reader.f32()

    def _parse_bone_rotation(self):
        self.bone.rotation.x = self.reader.f32()
        self.bone.rotation.y = self.reader.f32()
        self.bone.rotation.z = self.reader.f32()
