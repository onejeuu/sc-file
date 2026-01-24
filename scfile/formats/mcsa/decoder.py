from scfile.consts import Factor, FileSignature, McsaModel, McsaUnits
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.animation import AnimationClip
from scfile.structures.flags import Flag
from scfile.structures.mesh import LocalBoneId, ModelMesh, SkeletonBoneId
from scfile.structures.skeleton import SkeletonBone

from .exceptions import McsaBoneLinksError, McsaVersionUnsupported
from .io import McsaFileIO
from .versions import SUPPORTED_VERSIONS, VERSION_FLAGS


class McsaDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCSA
    order = ByteOrder.LITTLE
    signature = FileSignature.MCSA

    _content = ModelContent

    def to_obj(self):
        from scfile.formats.obj.encoder import ObjEncoder

        return self.convert_to(ObjEncoder)

    def to_glb(self):
        from scfile.formats.glb.encoder import GlbEncoder

        return self.convert_to(GlbEncoder)

    def to_dae(self):
        from scfile.formats.dae.encoder import DaeEncoder

        return self.convert_to(DaeEncoder)

    def to_ms3d(self):
        from scfile.formats.ms3d.encoder import Ms3dEncoder

        return self.convert_to(Ms3dEncoder)

    def parse(self):
        self._parse_header()
        self._parse_meshes()

        if self.data.flags[Flag.SKELETON] and self.options.parse_skeleton:
            self._parse_skeleton()

            if self.options.parse_animation and not self.is_eof():
                self._parse_animation()

    def _parse_header(self):
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self):
        self.data.version = self._readb(F.F32)

        if self.data.version not in SUPPORTED_VERSIONS:
            raise McsaVersionUnsupported(self.path, self.data.version)

    def _parse_flags(self):
        flags_count = VERSION_FLAGS.get(self.data.version)

        if not flags_count:
            raise McsaVersionUnsupported(self.path, self.data.version)

        for index in range(flags_count):
            self.data.flags[index] = self._readb(F.BOOL)

    def _parse_scales(self):
        self.data.scene.scale.position = self._readb(F.F32)

        if self.data.flags[Flag.UV]:
            self.data.scene.scale.texture = self._readb(F.F32)

        # ! Unknown Scale
        if self.data.flags[Flag.NORMALS] and self.data.version >= 10.0:
            self.data.scene.scale.unknown = self._readb(F.F32)

    def _parse_meshes(self):
        self.data.scene.count.meshes = self._readb(F.I32)

        for _ in range(self.data.scene.count.meshes):
            self._parse_mesh()

    def _skip_vertices(self, mesh: ModelMesh, units: int):
        self.read(mesh.count.vertices * units)

    def _parse_mesh(self):
        mesh = ModelMesh()

        # Name & Material
        mesh.name = self._readutf8()
        mesh.material = self._readutf8()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            mesh.count.links = self._readb(F.U8)
            mesh.count.bones = self._readb(F.U8)

            # Local bones mapping
            for index in range(mesh.count.bones):
                mesh.bones[LocalBoneId(index)] = SkeletonBoneId(self._readb(F.U8))

        # Geometry counts
        mesh.count.vertices = self._readcount("vertices")
        mesh.count.polygons = self._readcount("polygons")

        # ? Not exported
        if self.data.flags[Flag.UV]:
            self.data.scene.scale.filtering = self._readb(F.F32)

        # Default origins
        if self.data.version >= 10.0:
            mesh.origin.rotation = self._readarray(F.F32, 3)
            mesh.origin.position = self._readarray(F.F32, 3)

        # Default scale
        if self.data.version >= 11.0:
            mesh.origin.scale = self._readb(F.F32)

        # Geometric vertices
        self._parse_positions(mesh)

        # Texture coordinates
        if self.data.flags[Flag.UV]:
            self._parse_textures(mesh)

        # ! Data Unconfirmed
        # ? Not parsed
        if self.data.flags[Flag.UNKNOWN_5]:
            self._skip_vertices(mesh, units=4)

        # Vertex normals
        if self.data.flags[Flag.NORMALS]:
            self._parse_normals(mesh)

        # ! Data Unconfirmed
        # ? Not parsed
        if self.data.flags[Flag.UNKNOWN_4]:
            self._skip_vertices(mesh, units=4)

        # Vertex links
        if self.data.flags[Flag.SKELETON]:
            self._parse_links(mesh)

        # ! Data Unconfirmed
        # ? Not parsed
        if self.data.flags[Flag.UNKNOWN_6]:
            self._skip_vertices(mesh, units=4)

        # Polygon faces
        mesh.polygons = self._readpolygons(mesh.count.polygons)

        self.data.scene.meshes.append(mesh)

    def _parse_positions(self, mesh: ModelMesh):
        mesh.positions = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.POSITIONS,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.position,
        )[:, :3]

    def _parse_textures(self, mesh: ModelMesh):
        mesh.textures = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.TEXTURES,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.texture,
        )

    def _parse_normals(self, mesh: ModelMesh):
        mesh.normals = self._readvertex(
            fmt=F.I8,
            factor=Factor.I8,
            units=McsaUnits.NORMALS,
            count=mesh.count.vertices,
        )[:, :3]

    def _parse_links(self, mesh: ModelMesh):
        match mesh.count.links:
            case 0:
                pass
            case 1 | 2:
                self._parse_packed_links(mesh)
            case 3 | 4:
                self._parse_plain_links(mesh)
            case _:
                raise McsaBoneLinksError(self.path, mesh.count.links)

    def _parse_packed_links(self, mesh: ModelMesh):
        if self.options.parse_skeleton:
            links = self._readpackedlinks(mesh.count.vertices, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self._skip_vertices(mesh, units=4)

    def _parse_plain_links(self, mesh: ModelMesh):
        if self.options.parse_skeleton:
            links = self._readplainlinks(mesh.count.vertices, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self._skip_vertices(mesh, units=8)

    def _parse_skeleton(self):
        self.data.scene.count.bones = self._readb(F.U8)

        for index in range(self.data.scene.count.bones):
            self._parse_bone(index)

    def _parse_bone(self, index: int):
        bone = SkeletonBone()

        bone.id = index
        bone.name = self._readutf8()

        # ? Bone is root if parent_id points to itself
        # ? self-reference would cause invalid recursion
        parent_id = self._readb(F.U8)
        bone.parent_id = parent_id if parent_id != index else McsaModel.ROOT_BONE_ID

        bone.position, bone.rotation = self._readbone()

        self.data.scene.skeleton.bones.append(bone)

    def _parse_animation(self):
        self.data.scene.count.clips = self._readb(F.I32)

        for _ in range(self.data.scene.count.clips):
            self._parse_clip()

    def _parse_clip(self):
        clip = AnimationClip()

        clip.name = self._readutf8()
        clip.frames = self._readb(F.U32)
        clip.rate = self._readb(F.F32)
        clip.transforms = self._readclip(clip.frames, self.data.scene.count.bones)

        self.data.scene.animation.clips.append(clip)
