from typing import Any

from scfile.consts import Factor, McsaModel, McsaSize
from scfile.core.base.parser import FileParser
from scfile.core.data.model import ModelData
from scfile.enums import StructFormat as F
from scfile.io.mcsa import McsaFileIO
from scfile.utils.model.mesh import ModelMesh
from scfile.utils.model.skeleton import SkeletonBone
from scfile.utils.model.vertex import Joint

from .flags import Flag
from .versions import SUPPORTED_VERSIONS, VERSION_FLAGS


class McsaParser(FileParser[McsaFileIO, ModelData]):
    def parse(self):
        self.parse_header()
        self.parse_meshes()

        if self.data.flags[Flag.SKELETON]:
            self.parse_skeleton()

    @property
    def model(self):
        return self.data.model

    def parse_header(self):
        self.parse_version()
        self.parse_flags()
        self.parse_scales()

    def parse_version(self):
        self.data.version = self.f.readb(F.F32)

        if self.data.version not in SUPPORTED_VERSIONS:
            raise Exception(self.path, self.data.version)

    def parse_flags(self):
        flags_count = VERSION_FLAGS.get(self.data.version)

        if not flags_count:
            raise Exception(self.path, self.data.version)

        for index in range(flags_count):
            self.data.flags[index] = self.f.readb(F.BOOL)

    def parse_scales(self):
        self.model.scale.position = self.f.readb(F.F32)

        if self.data.flags[Flag.TEXTURE]:
            self.model.scale.texture = self.f.readb(F.F32)

        if self.data.flags[Flag.NORMALS] and self.data.version >= 10.0:
            self.model.scale.normals = self.f.readb(F.F32)

    def parse_meshes(self):
        meshes_count = self.f.readb(F.U32)

        for _ in range(meshes_count):
            self.parse_mesh()

    def parse_mesh(self):
        mesh = ModelMesh()

        # Name & Material
        mesh.name = self.f.readstring()
        mesh.material = self.f.readstring()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            self.parse_bone_indexes(mesh)

        # Geometry counts
        mesh.count.vertices = self.f.readcount()
        mesh.count.polygons = self.f.readcount()
        mesh.allocate_geometry()

        # ! unknown, unconfirmed
        if self.data.flags[Flag.TEXTURE]:
            self.model.scale.weight = self.f.readb(F.F32)

        # ! unknown, unconfirmed
        if self.data.version >= 10.0:
            self.skip_locals()

        # Geometric vertices
        self.parse_position(mesh)

        # Texture coordinates
        if self.data.flags[Flag.TEXTURE]:
            self.parse_texture(mesh)

        # ! unconfirmed
        if self.data.flags[Flag.BITANGENTS]:
            self.skip_vertices(mesh, size=4)

        # Vertex normals
        if self.data.flags[Flag.NORMALS]:
            self.parse_normals(mesh)

        # ! unconfirmed
        if self.data.flags[Flag.TANGENTS]:
            self.skip_vertices(mesh, size=4)

        # Vertex links
        if self.data.flags[Flag.SKELETON]:
            self.skip_links(mesh)

        # Vertex colors
        if self.data.flags[Flag.COLORS]:
            self.skip_colors(mesh)

        # Polygon faces
        self.parse_polygons(mesh)

        self.model.meshes.append(mesh)

    def parse_bone_indexes(self, mesh: ModelMesh):
        mesh.count.max_links = self.f.readb(F.U8)
        mesh.count.bones = self.f.readb(F.U8)

        for index in range(mesh.count.bones):
            mesh.bones[index] = self.f.readb(F.U8)

    def skip_locals(self):
        self.f.read(24)  # ? 6 floats

        if self.data.version >= 11.0:
            self.f.read(4)

    def parse_position(self, mesh: ModelMesh):
        count = mesh.count.vertices
        scale = self.model.scale.position
        xyzw = self.f.readvertex(F.I16, Factor.I16 + 1, McsaSize.POSITION, count, scale)

        for vertex, (x, y, z, _) in zip(mesh.vertices, xyzw):
            vertex.position.x = x
            vertex.position.y = y
            vertex.position.z = z

    def parse_texture(self, mesh: ModelMesh):
        count = mesh.count.vertices
        scale = self.model.scale.texture
        uv = self.f.readvertex(F.I16, Factor.I16, McsaSize.TEXTURE, count, scale)

        for vertex, (u, v) in zip(mesh.vertices, uv):
            vertex.texture.u = u
            vertex.texture.v = v

    def parse_normals(self, mesh: ModelMesh):
        count = mesh.count.vertices
        xyzw = self.f.readvertex(F.I8, Factor.I8, McsaSize.NORMALS, count)

        for vertex, (x, y, z, _) in zip(mesh.vertices, xyzw):
            vertex.normals.x = x
            vertex.normals.y = y
            vertex.normals.z = z

    def skip_links(self, mesh: ModelMesh):
        match mesh.count.max_links:
            case 0:
                pass
            case 1 | 2:
                links = self.f.readlinkspacked(mesh.count.vertices)
                self.load_links(mesh, links)
                mesh.count.links = 2
            case 3 | 4:
                links = self.f.readlinksplains(mesh.count.vertices)
                self.load_links(mesh, links)
                mesh.count.links = 4
            case _:
                raise Exception(f"Unknown links count: {mesh.count.max_links}")

    def load_links(self, mesh: ModelMesh, links: Any):
        link_ids, link_weights = links

        for vertex, ids, weights in zip(mesh.vertices, link_ids, link_weights):
            vertex.joints = dict(zip(ids, weights))

    def skip_colors(self, mesh: ModelMesh):
        self.skip_vertices(mesh, size=4)

    def parse_polygons(self, mesh: ModelMesh):
        abc = self.f.readpolygons(mesh.count.polygons)

        for polygon, (a, b, c) in zip(mesh.polygons, abc):
            polygon.a = a
            polygon.b = b
            polygon.c = c

    def skip_vertices(self, mesh: ModelMesh, size: int):
        self.f.read(mesh.count.vertices * size)

    def parse_skeleton(self):
        bones_count = self.f.readb(F.U8)

        for index in range(bones_count):
            self.parse_bone(index)

    def parse_bone(self, index: int) -> None:
        bone = SkeletonBone()

        bone.id = index
        bone.name = self.f.readstring()

        parent_id = self.f.readb(F.U8)
        bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        self.parse_bone_position(bone)
        self.parse_bone_rotation(bone)

        self.model.skeleton.bones.append(bone)

    def parse_bone_position(self, bone: SkeletonBone):
        x, y, z = self.f.readbonedata()

        bone.position.x = x
        bone.position.y = y
        bone.position.z = z

    def parse_bone_rotation(self, bone: SkeletonBone):
        x, y, z = self.f.readbonedata()

        bone.rotation.x = x
        bone.rotation.y = y
        bone.rotation.z = z
