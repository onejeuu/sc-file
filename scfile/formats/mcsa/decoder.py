from collections import defaultdict
from dataclasses import dataclass

from scfile import formats
from scfile.consts import Factor, FileSignature, ModelDefaults
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import Flag

from .consts import McsaUnits
from .exceptions import McsaCountsLimit, McsaVersionUnsupported
from .io import McsaFileIO
from .versions import SUPPORTED_VERSIONS, VERSION_MAP


@dataclass
class MeshCounts:
    vertices: int = 0
    polygons: int = 0
    max_influences: int = 0
    local_bones: int = 0


class McsaDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCSA
    signature = FileSignature.MCSA
    order = ByteOrder.LITTLE

    _content = ModelContent

    def as_obj(self):
        return self.convert_to(formats.obj.ObjEncoder)

    def as_glb(self):
        return self.convert_to(formats.glb.GlbEncoder)

    def as_fbx(self):
        return self.convert_to(formats.fbx.FbxEncoder)

    def as_dae(self):
        return self.convert_to(formats.dae.DaeEncoder)

    def as_ms3d(self):
        return self.convert_to(formats.ms3d.Ms3dEncoder)

    def parse(self):
        self._parse_header()
        self._parse_meshes()

        if self.data.flags[Flag.SKELETON] and self.options.skeleton:
            self._parse_skeleton()

            if self.options.animation and not self.is_eof():
                self._parse_animation()

    def _parse_header(self):
        self._parse_version()
        self._parse_flags()
        self._parse_scales()

    def _parse_version(self):
        self.data.version = self._readb(F.F32)

        if self.data.version not in SUPPORTED_VERSIONS:
            raise McsaVersionUnsupported(self.location, self.data.version)

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
        self.ctx["COUNT_MESHES"] = self._readb(F.I32)

        for _ in range(self.ctx["COUNT_MESHES"]):
            self._parse_mesh()

    def _parse_mesh(self):
        mesh = S.ModelMesh()

        # Name & Material
        mesh.name = self._readutf8()
        mesh.material = self._readutf8()

        counts = MeshCounts()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            counts.max_influences = self._readb(F.U8)
            counts.local_bones = self._readb(F.U8)

            # Local bones mapping
            for index in range(counts.local_bones):
                mesh.bones[S.LocalBoneId(index)] = S.SkeletonBoneId(self._readb(F.U8))

        # Geometry counts
        counts.vertices = self._parse_count("vertices")

        if self.data.version >= 12.0:
            mesh.quads = self._readb(F.BOOL)

        counts.polygons = self._parse_count("polygons")

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
        self._parse_positions(mesh, counts.vertices)

        # Texture coordinates (Atlas)
        if self.data.flags[Flag.UV]:
            self._parse_uv1(mesh, counts.vertices)

        # Texture coordinates (AO)
        if self.data.flags[Flag.UV2]:
            self._parse_uv2(mesh, counts.vertices)

        # Vertices normals
        if self.data.flags[Flag.NORMALS]:
            mesh.normals = self._readnormals(counts.vertices)

        # ? Not parsed
        # Vertices tangents
        if self.data.flags[Flag.TANGENTS]:
            mesh.tangents = self._readtangents(counts.vertices)

        # ? Not parsed
        # Vertices rgba colors
        if self.data.flags[Flag.COLORS]:
            self.skip(counts.vertices * 4)

        # Vertices bones links
        if self.data.flags[Flag.SKELETON]:
            self._parse_links(mesh, counts.vertices, counts.max_influences)

        # Polygon faces
        mesh.polygons = self._readpolygons(counts.polygons, mesh.quads)

        self.data.scene.meshes.append(mesh)

    def _parse_count(self, type: str) -> int:
        count = self._readb(F.U32)

        # ? Prevent memory overflow
        if count > ModelDefaults.GEOMETRY_LIMIT:
            raise McsaCountsLimit(self.location, type, count)

        return count

    def _parse_positions(self, mesh: S.ModelMesh, count: int):
        mesh.vertices = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.POSITIONS,
            scale=self.data.scene.scale.position,
            count=count,
        )[:, :3]

    def _parse_uv1(self, mesh: S.ModelMesh, count: int):
        mesh.uv1 = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.TEXTURES,
            scale=self.data.scene.scale.uv,
            count=count,
        )

    def _parse_uv2(self, mesh: S.ModelMesh, count: int):
        mesh.uv2 = self._readvertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=McsaUnits.TEXTURES,
            scale=self.data.scene.scale.uv2,
            count=count,
        )

    def _parse_links(self, mesh: S.ModelMesh, count: int, max_influences: int):
        match max_influences:
            case 1 | 2:
                self._parse_packed_links(mesh, count)
            case 3 | 4:
                self._parse_plain_links(mesh, count)
            case _:
                return

    def _parse_packed_links(self, mesh: S.ModelMesh, count: int):
        if self.options.skeleton:
            links = self._readpackedlinks(count, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self.skip(count * 4)

    def _parse_plain_links(self, mesh: S.ModelMesh, count: int):
        if self.options.skeleton:
            links = self._readplainlinks(count, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self.skip(count * 4)

    def _parse_skeleton(self):
        self.ctx["COUNT_BONES"] = self._readb(F.U8)

        for index in range(self.ctx["COUNT_BONES"]):
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
        self.ctx["COUNT_CLIPS"] = self._readb(F.I32)

        for _ in range(self.ctx["COUNT_CLIPS"]):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self._readutf8()
        clip.frames = self._readb(F.U32)
        clip.rate = self._readb(F.F32)

        rotations, translations = self._readclip(clip.frames, self.ctx["COUNT_BONES"])
        clip.rotations = rotations
        clip.translations = translations

        self.data.scene.animation.clips.append(clip)
