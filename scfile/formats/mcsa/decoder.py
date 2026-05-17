from collections import defaultdict

from scfile.consts import Factor, FileSignature, ModelDefaults
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import Flag

from .consts import McsaUnits
from .exceptions import McsaBoneLinksError, McsaVersionUnsupported
from .io import McsaFileIO
from .versions import SUPPORTED_VERSIONS, VERSION_MAP


class McsaDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCSA
    signature = FileSignature.MCSA
    order = ByteOrder.LITTLE

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
        latest = max(VERSION_MAP.keys())
        mapping = VERSION_MAP.get(self.data.version, VERSION_MAP[latest])

        self.data.flags = defaultdict(bool, {flag: bool(self._readb(F.BOOL)) for flag in mapping})

    def _parse_scales(self):
        self.data.scene.scale.position = self._readb(F.F32)

        if self.data.flags[Flag.UV]:
            self.data.scene.scale.uv = self._readb(F.F32)

        if self.data.flags[Flag.UV2]:
            self.data.scene.scale.uv2 = self._readb(F.F32)

    def _parse_meshes(self):
        self.data.scene.count.meshes = self._readb(F.I32)

        for _ in range(self.data.scene.count.meshes):
            self._parse_mesh()

    def _skip_vertices(self, mesh: S.ModelMesh, units: int):
        self.read(mesh.count.vertices * units)

    def _parse_mesh(self):
        mesh = S.ModelMesh()

        # Name & Material
        mesh.name = self._readutf8()
        mesh.material = self._readutf8()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            mesh.count.links = self._readb(F.U8)
            mesh.count.bones = self._readb(F.U8)

            # Local bones mapping
            for index in range(mesh.count.bones):
                mesh.bones[S.LocalBoneId(index)] = S.SkeletonBoneId(self._readb(F.U8))

        # Geometry counts
        mesh.count.vertices = self._readcount("vertices")

        if self.data.version >= 12.0:
            mesh.quads = self._readb(F.BOOL)

        mesh.count.polygons = self._readcount("polygons")

        # ? Not exported
        if self.data.flags[Flag.UV]:
            self.data.scene.scale.filtering = self._readb(F.F32)

        # Default origins
        if self.data.version >= 10.0:
            mesh.bounds.min = self._readarray(F.F32, 3)
            mesh.bounds.max = self._readarray(F.F32, 3)

        # Default scale
        if self.data.version >= 11.0:
            mesh.bounds.radius = self._readb(F.F32)

        # Vertices geometric
        self._parse_positions(mesh)

        # Texture coordinates (Atlas)
        if self.data.flags[Flag.UV]:
            self._parse_uv1(mesh)

        # Texture coordinates (AO)
        if self.data.flags[Flag.UV2]:
            self._parse_uv2(mesh)

        # Vertices normals
        if self.data.flags[Flag.NORMALS]:
            mesh.normals = self._readnormals(mesh.count.vertices)

        # ? Not parsed
        # Vertices tangents
        if self.data.flags[Flag.TANGENTS]:
            mesh.tangents = self._readtangents(mesh.count.vertices)

        # ? Not parsed
        # Vertices rgba colors
        if self.data.flags[Flag.COLORS]:
            self._skip_vertices(mesh, units=4)

        # Vertices bones links
        if self.data.flags[Flag.SKELETON]:
            self._parse_links(mesh)

        # Polygon faces
        mesh.polygons = self._readpolygons(mesh.count.polygons, mesh.quads)

        self.data.scene.meshes.append(mesh)

    def _parse_positions(self, mesh: S.ModelMesh):
        mesh.positions = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.POSITIONS,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.position,
        )[:, :3]

    def _parse_uv1(self, mesh: S.ModelMesh):
        mesh.uv1 = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.TEXTURES,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.uv,
        )

    def _parse_uv2(self, mesh: S.ModelMesh):
        mesh.uv2 = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.TEXTURES,
            count=mesh.count.vertices,
            scale=self.data.scene.scale.uv2,
        )

    def _parse_links(self, mesh: S.ModelMesh):
        match mesh.count.links:
            case 0:
                pass
            case 1 | 2:
                self._parse_packed_links(mesh)
            case 3 | 4:
                self._parse_plain_links(mesh)
            case _:
                raise McsaBoneLinksError(self.path, mesh.count.links)

    def _parse_packed_links(self, mesh: S.ModelMesh):
        if self.options.parse_skeleton:
            links = self._readpackedlinks(mesh.count.vertices, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self._skip_vertices(mesh, units=4)

    def _parse_plain_links(self, mesh: S.ModelMesh):
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
        bone = S.SkeletonBone()

        bone.id = index
        bone.name = self._readutf8()

        # ? Bone is root if parent_id points to itself
        # ? self-reference would cause invalid recursion
        parent_id = self._readb(F.U8)
        bone.parent_id = parent_id if parent_id != index else ModelDefaults.ROOT_BONE_ID

        bone.position, bone.rotation = self._readbone()

        self.data.scene.skeleton.bones.append(bone)

    def _parse_animation(self):
        self.data.scene.count.clips = self._readb(F.I32)

        for _ in range(self.data.scene.count.clips):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self._readutf8()
        clip.frames = self._readb(F.U32)
        clip.rate = self._readb(F.F32)

        rotations, translations = self._readclip(clip.frames, self.data.scene.count.bones)
        clip.rotations = rotations
        clip.translations = translations

        self.data.scene.animation.clips.append(clip)
