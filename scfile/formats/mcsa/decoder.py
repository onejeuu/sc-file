from typing import Any

from scfile import exceptions as exc
from scfile.consts import Factor, FileSignature, McsaModel, McsaSize
from scfile.core.context import ModelContent, ModelOptions
from scfile.core.decoder import FileDecoder
from scfile.core.io.formats.mcsa import McsaFileIO
from scfile.enums import ByteOrder, FileFormat
from scfile.enums import StructFormat as F
from scfile.formats.dae.encoder import DaeEncoder
from scfile.formats.glb.encoder import GlbEncoder
from scfile.formats.ms3d.encoder import Ms3dEncoder
from scfile.formats.obj.encoder import ObjEncoder
from scfile.structures.animation import (
    AnimationClip,
    AnimationFrame,
    AnimationTransforms,
)
from scfile.structures.mesh import LocalBoneId, ModelMesh, SkeletonBoneId
from scfile.structures.skeleton import SkeletonBone

from .flags import Flag
from .versions import SUPPORTED_VERSIONS, VERSION_FLAGS


class McsaDecoder(FileDecoder[ModelContent, ModelOptions], McsaFileIO):
    format = FileFormat.MCSA
    order = ByteOrder.LITTLE
    signature = FileSignature.MCSA

    _content = ModelContent
    _options = ModelOptions

    def to_dae(self):
        return self.convert_to(DaeEncoder)

    def to_obj(self):
        return self.convert_to(ObjEncoder)

    def to_gltf(self):
        return self.convert_to(GlbEncoder)

    def to_ms3d(self):
        return self.convert_to(Ms3dEncoder)

    def parse(self):
        self.parse_header()
        self.parse_meshes()

        if self.data.flags[Flag.SKELETON] and self.options.parse_skeleton:
            self.parse_skeleton()

            if self.options.parse_animations:
                self.parse_animations()

    def parse_header(self):
        self.parse_version()
        self.parse_flags()
        self.parse_scales()

    def parse_version(self):
        self.data.version = self.readb(F.F32)

        if self.data.version not in SUPPORTED_VERSIONS:
            raise exc.McsaUnsupportedVersion(self.path, self.data.version)

    def parse_flags(self):
        flags_count = VERSION_FLAGS.get(self.data.version)

        if not flags_count:
            raise exc.McsaUnsupportedVersion(self.path, self.data.version)

        for index in range(flags_count):
            self.data.flags[index] = self.readb(F.BOOL)

    def parse_scales(self):
        self.data.scene.scale.position = self.readb(F.F32)

        if self.data.flags[Flag.TEXTURE]:
            self.data.scene.scale.texture = self.readb(F.F32)

        # ! unknown
        if self.data.flags[Flag.NORMALS] and self.data.version >= 10.0:
            self.data.scene.scale.normals = self.readb(F.F32)

    def parse_meshes(self):
        meshes_count = self.readb(F.U32)

        for _ in range(meshes_count):
            self.parse_mesh()

    def parse_mesh(self):
        mesh = ModelMesh()

        # Name & Material
        mesh.name = self.readstring()
        mesh.material = self.readstring()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            self.parse_links_count(mesh)
            self.parse_local_bones(mesh)

        # Geometry counts
        mesh.count.vertices = self.readcount()
        mesh.count.polygons = self.readcount()
        mesh.allocate_geometry()

        if self.data.flags[Flag.TEXTURE]:
            self.data.scene.scale.filtering = self.readb(F.F32)

        if self.data.version >= 10.0:
            self.parse_defaults(mesh)

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
            self.parse_links(mesh)

        # TODO: optional parse and export
        # Vertex colors
        if self.data.flags[Flag.COLORS]:
            self.skip_colors(mesh)

        # Polygon faces
        self.parse_polygons(mesh)

        self.data.meshes.append(mesh)

    def parse_links_count(self, mesh: ModelMesh):
        mesh.count.max_links = self.readb(F.U8)
        mesh.count.local_bones = self.readb(F.U8)

    def parse_local_bones(self, mesh: ModelMesh):
        for index in range(mesh.count.local_bones):
            mesh.bones_mapping[LocalBoneId(index)] = SkeletonBoneId(self.readb(F.U8))

    def parse_defaults(self, mesh: ModelMesh):
        for x, y, z in self.readdefault():
            mesh.default.rotation.x = x
            mesh.default.rotation.y = y
            mesh.default.rotation.z = z

        for x, y, z in self.readdefault():
            mesh.default.position.x = x
            mesh.default.position.y = y
            mesh.default.position.z = z

        if self.data.version >= 11.0:
            mesh.default.scale = self.readb(F.F32)

    def parse_position(self, mesh: ModelMesh):
        count = mesh.count.vertices
        scale = self.data.scene.scale.position
        xyzw = self.readvertex(F.I16, Factor.I16 + 1, McsaSize.POSITION, count, scale)

        for vertex, (x, y, z, _) in zip(mesh.vertices, xyzw):
            vertex.position.x = x
            vertex.position.y = y
            vertex.position.z = z

    def parse_texture(self, mesh: ModelMesh):
        count = mesh.count.vertices
        scale = self.data.scene.scale.texture
        uv = self.readvertex(F.I16, Factor.I16, McsaSize.TEXTURE, count, scale)

        for vertex, (u, v) in zip(mesh.vertices, uv):
            vertex.texture.u = u
            vertex.texture.v = v

    def parse_normals(self, mesh: ModelMesh):
        count = mesh.count.vertices
        xyzw = self.readvertex(F.I8, Factor.I8, McsaSize.NORMALS, count)

        for vertex, (x, y, z, _) in zip(mesh.vertices, xyzw):
            vertex.normals.x = x
            vertex.normals.y = y
            vertex.normals.z = z

    def parse_links(self, mesh: ModelMesh):
        match mesh.count.max_links:
            case 0:
                pass

            case 1 | 2:
                if self.options.parse_skeleton:
                    self.parse_packed_links(mesh)
                else:
                    self.skip_vertices(mesh, size=4)

            case 3 | 4:
                if self.options.parse_skeleton:
                    self.parse_plain_links(mesh)
                else:
                    self.skip_vertices(mesh, size=8)

            case _:
                raise exc.McsaUnknownLinkCount(self.path, mesh.count.max_links)

    def parse_packed_links(self, mesh: ModelMesh):
        links = self.readlinkspacked(mesh.count.vertices, mesh.bones_mapping)
        self.load_links(mesh, links)

    def parse_plain_links(self, mesh: ModelMesh):
        links = self.readlinksplains(mesh.count.vertices, mesh.bones_mapping)
        self.load_links(mesh, links)

    def load_links(self, mesh: ModelMesh, links: Any):
        link_ids, link_weights = links

        for vertex, ids, weights in zip(mesh.vertices, link_ids, link_weights):
            vertex.bone_ids = ids
            vertex.bone_weights = weights

    def skip_colors(self, mesh: ModelMesh):
        self.skip_vertices(mesh, size=4)

    def parse_polygons(self, mesh: ModelMesh):
        abc = self.readpolygons(mesh.count.polygons)

        for polygon, (a, b, c) in zip(mesh.polygons, abc):
            polygon.a = a
            polygon.b = b
            polygon.c = c

    def skip_vertices(self, mesh: ModelMesh, size: int):
        self.read(mesh.count.vertices * size)

    def parse_skeleton(self):
        bones_count = self.readb(F.U8)

        for index in range(bones_count):
            self.parse_bone(index)

    def parse_bone(self, index: int) -> None:
        bone = SkeletonBone()

        bone.id = index
        bone.name = self.readstring()

        parent_id = self.readb(F.U8)
        bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        self.parse_bone_position(bone)
        self.parse_bone_rotation(bone)

        self.data.skeleton.bones.append(bone)

    def parse_bone_position(self, bone: SkeletonBone):
        x, y, z = self.readbonedata()

        bone.position.x = x
        bone.position.y = y
        bone.position.z = z

    def parse_bone_rotation(self, bone: SkeletonBone):
        x, y, z = self.readbonedata()

        bone.rotation.x = x
        bone.rotation.y = y
        bone.rotation.z = z

    def parse_animations(self):
        animations_count = self.readb(F.U32)

        for _ in range(animations_count):
            self.parse_animation()

    def parse_animation(self):
        clip = AnimationClip()

        clip.name = self.readstring()
        clip.frames = self.readb(F.U32)
        clip.rate = self.readb(F.F32)

        self.parse_animation_frames(clip)

    def parse_animation_frames(self, clip: AnimationClip):
        # ! WIP

        # print(clip.name)

        for _ in range(len(self.data.skeleton.bones)):
            transform = AnimationTransforms()

            # print()
            # print("transform", _)

            for _ in range(clip.frames):
                frame = AnimationFrame()
                (rx, ry, rz, rw), (tx, ty, tz) = self.readcliptransforms()

                # print((rx, ry, rz, rw), (tx, ty, tz))

                frame.translation.x = tx
                frame.translation.y = ty
                frame.translation.z = tz

                frame.rotation.x = rx
                frame.rotation.y = ry
                frame.rotation.z = rz
                frame.rotation.w = rw

                transform.frames.append(frame)

            clip.transforms.append(transform)

        self.data.animation.clips.append(clip)
