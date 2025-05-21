from scfile.consts import Factor, FileSignature, McsaModel, McsaSize
from scfile.core.context import ModelContent
from scfile.core.decoder import FileDecoder
from scfile.enums import ByteOrder, FileFormat
from scfile.enums import StructFormat as F
from scfile.formats.dae.encoder import DaeEncoder
from scfile.formats.glb.encoder import GlbEncoder
from scfile.formats.ms3d.encoder import Ms3dEncoder
from scfile.formats.obj.encoder import ObjEncoder
from scfile.structures.animation import AnimationClip
from scfile.structures.mesh import LocalBoneId, ModelMesh, SkeletonBoneId
from scfile.structures.skeleton import SkeletonBone

from .exceptions import McsaBoneLinksError, McsaVersionUnsupported
from .flags import Flag
from .io import McsaFileIO
from .versions import SUPPORTED_VERSIONS, VERSION_FLAGS


class McsaDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCSA
    order = ByteOrder.LITTLE
    signature = FileSignature.MCSA

    _content = ModelContent

    def to_obj(self):
        return self.convert_to(ObjEncoder)

    def to_glb(self):
        return self.convert_to(GlbEncoder)

    def to_dae(self):
        return self.convert_to(DaeEncoder)

    def to_ms3d(self):
        return self.convert_to(Ms3dEncoder)

    def parse(self):
        self.parse_header()
        self.parse_meshes()

        if self.data.flags[Flag.SKELETON] and self.options.parse_skeleton:
            self.parse_skeleton()

            if self.options.parse_animation and not self.is_eof():
                self.parse_animation()

    def parse_header(self):
        self.parse_version()
        self.parse_flags()
        self.parse_scales()

    def parse_version(self):
        self.data.version = self.readb(F.F32)

        if self.data.version not in SUPPORTED_VERSIONS:
            raise McsaVersionUnsupported(self.path, self.data.version)

    def parse_flags(self):
        flags_count = VERSION_FLAGS.get(self.data.version)

        if not flags_count:
            raise McsaVersionUnsupported(self.path, self.data.version)

        for index in range(flags_count):
            self.data.flags[index] = self.readb(F.BOOL)

    def parse_scales(self):
        self.data.scene.scale.position = self.readb(F.F32)

        if self.data.flags[Flag.UV]:
            self.data.scene.scale.texture = self.readb(F.F32)

        # ! Unknown Scale
        if self.data.flags[Flag.NORMALS] and self.data.version >= 10.0:
            self.data.scene.scale.unknown = self.readb(F.F32)

    def parse_meshes(self):
        self.data.scene.count.meshes = self.readb(F.I32)

        if self.data.scene.count.meshes > 0:
            for _ in range(self.data.scene.count.meshes):
                self.parse_mesh()

    def parse_mesh(self):
        mesh = ModelMesh()

        # Name & Material
        mesh.name = self.readutf8()
        mesh.material = self.readutf8()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            mesh.count.links = self.readb(F.U8)
            mesh.count.bones = self.readb(F.U8)

            # Local bones mapping
            for index in range(mesh.count.bones):
                mesh.bones[LocalBoneId(index)] = SkeletonBoneId(self.readb(F.U8))

        # Geometry counts
        mesh.count.vertices = self.readcount("vertices")
        mesh.count.polygons = self.readcount("polygons")

        # ? Not exported
        if self.data.flags[Flag.UV]:
            self.data.scene.scale.filtering = self.readb(F.F32)

        # Default origins
        # ? Not exported
        if self.data.version >= 10.0:
            self.read(4 * 6)

        # Default scale
        # ? Not exported
        if self.data.version >= 11.0:
            self.read(4)

        # Geometric vertices
        self.parse_positions(mesh)

        # Texture coordinates
        if self.data.flags[Flag.UV]:
            self.parse_textures(mesh)

        # ! Data Unconfirmed
        # ? Not parsed
        if self.data.flags[Flag.UNKNOWN_B]:
            self.skip_vertices(mesh, size=4)

        # Vertex normals
        if self.data.flags[Flag.NORMALS]:
            self.parse_normals(mesh)

        # ! Data Unconfirmed
        # ? Not parsed
        if self.data.flags[Flag.UNKNOWN_A]:
            self.skip_vertices(mesh, size=4)

        # Vertex links
        if self.data.flags[Flag.SKELETON]:
            self.parse_links(mesh)

        # Vertex colors
        # ? Not parsed
        if self.data.flags[Flag.COLORS]:
            self.skip_vertices(mesh, size=4)

        # Polygon faces
        mesh.polygons = self.readpolygons(mesh.count.polygons)

        self.data.scene.meshes.append(mesh)

    def skip_vertices(self, mesh: ModelMesh, size: int):
        self.read(mesh.count.vertices * size)

    def parse_positions(self, mesh: ModelMesh):
        mesh.positions = self.readvertex(
            dtype=F.F32,
            fmt=F.I16,
            factor=Factor.I16,
            size=McsaSize.POSITIONS,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.position,
        )[:, :3]

    def parse_textures(self, mesh: ModelMesh):
        mesh.textures = self.readvertex(
            dtype=F.F32,
            fmt=F.I16,
            factor=Factor.I16,
            size=McsaSize.TEXTURES,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.texture,
        )

    def parse_normals(self, mesh: ModelMesh):
        mesh.normals = self.readvertex(
            dtype=F.F32,
            fmt=F.I8,
            factor=Factor.I8,
            size=McsaSize.NORMALS,
            count=mesh.count.vertices,
        )[:, :3]

    def parse_links(self, mesh: ModelMesh):
        match mesh.count.links:
            case 0:
                pass
            case 1 | 2:
                self.parse_packed_links(mesh)
            case 3 | 4:
                self.parse_plain_links(mesh)
            case _:
                raise McsaBoneLinksError(self.path, mesh.count.links)

    def parse_packed_links(self, mesh: ModelMesh):
        if self.options.parse_skeleton:
            links = self.readpackedlinks(mesh.count.vertices, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self.skip_vertices(mesh, size=4)

    def parse_plain_links(self, mesh: ModelMesh):
        if self.options.parse_skeleton:
            links = self.readplainlinks(mesh.count.vertices, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self.skip_vertices(mesh, size=8)

    def parse_skeleton(self):
        self.data.scene.count.bones = self.readb(F.U8)

        for index in range(self.data.scene.count.bones):
            self.parse_bone(index)

    def parse_bone(self, index: int):
        bone = SkeletonBone()

        bone.id = index
        bone.name = self.readutf8()

        parent_id = self.readb(F.U8)
        bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID
        bone.position, bone.rotation = self.readbone()

        self.data.scene.skeleton.bones.append(bone)

    def parse_animation(self):
        self.data.scene.count.clips = self.readb(F.I32)

        if self.data.scene.count.clips > 0:
            for _ in range(self.data.scene.count.clips):
                self.parse_clip()

    def parse_clip(self):
        clip = AnimationClip()

        clip.name = self.readutf8()
        clip.frames = self.readb(F.U32)
        clip.rate = self.readb(F.F32)
        clip.transforms = self.readclip(clip.frames, self.data.scene.count.bones)

        self.data.scene.animation.clips.append(clip)
