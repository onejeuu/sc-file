from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from scfile import formats
from scfile.consts import Factor, FileSignature, ModelDefaults
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.exceptions import BinaryStructureError, ModelVersionError
from scfile.structures import models as S
from scfile.structures.models import Flag, ModelUnits as Units

from scfile.io.models import ModelReader
from .versions import SUPPORTED_VERSIONS, VERSION_MAP


@dataclass
class MeshCounts:
    vertices: int = 0
    polygons: int = 0
    max_influences: int = 0
    local_bones: int = 0
    blend_shapes: int = 0


class McsaDecoder(FileDecoder[ModelContent, ModelReader]):
    format = FileFormat.MCSA
    signature = FileSignature.MCSA
    order = ByteOrder.LITTLE

    content_factory = ModelContent
    io_factory = ModelReader

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

            if (
                self.options.animation
                and (self.ctx["COUNT_BONES"] > 0 or self.ctx["COUNT_CHANNELS"] > 0)
                and not self.io.eof()
            ):
                self._parse_animation()

    def _parse_header(self):
        self._parse_version()
        self._parse_flags()
        self._parse_scales()
        self.ctx["BLEND_SHAPE_CHANNELS"] = []

    def _parse_version(self):
        self.data.version = self.io.value(F.F32)

        if self.data.version not in SUPPORTED_VERSIONS:
            raise ModelVersionError(
                self.data.version,
                location=self.location,
                offset=self.io.tell(),
            )

    def _parse_flags(self):
        latest = max(VERSION_MAP.keys())
        mapping = VERSION_MAP.get(self.data.version, VERSION_MAP[latest])

        self.data.flags = defaultdict(bool, {flag: bool(self.io.value(F.BOOL)) for flag in mapping})

    def _parse_scales(self):
        self.data.scene.scale.position = self.io.value(F.F32)

        if self.data.flags[Flag.UV]:
            self.data.scene.scale.uv = self.io.value(F.F32)

        if self.data.flags[Flag.UV2]:
            self.data.scene.scale.uv2 = self.io.value(F.F32)

    def _parse_meshes(self):
        self.ctx["COUNT_MESHES"] = self.io.count(F.I32, Limit.MESHES)

        for _ in range(self.ctx["COUNT_MESHES"]):
            self._parse_mesh()

    def _parse_mesh(self):
        mesh = S.ModelMesh()

        # Name & Material
        mesh.name = self.io.string()
        mesh.material = self.io.string()

        counts = MeshCounts()

        # Skeleton bone indexes
        if self.data.flags[Flag.SKELETON]:
            counts.max_influences = self.io.value(F.U8)
            counts.local_bones = self.io.value(F.U8)

            # Local bones mapping
            for index in range(counts.local_bones):
                mesh.bones[S.LocalBoneId(index)] = S.SkeletonBoneId(self.io.value(F.U8))

        # Geometry counts
        counts.vertices = self.io.count(F.U32, Limit.VERTICES)

        if self.data.version >= 12.0:
            mesh.polygon_quads = self.io.value(F.BOOL)

        counts.polygons = self.io.count(F.U32, Limit.POLYGONS)

        channel_ids = self._parse_blend_shape_mapping(mesh, counts)

        # ? Not exported
        if self.data.flags[Flag.UV]:
            mesh.mip_factor = self.io.value(F.F32)

        if self.data.version >= 10.0:
            mesh.bounds.min = self.io.array(F.F32, 3)
            mesh.bounds.max = self.io.array(F.F32, 3)

        if self.data.version >= 11.0:
            mesh.bounds.radius = self.io.value(F.F32)

        # Vertices geometric
        self._parse_positions(mesh, counts.vertices)

        # Texture coordinates (atlas)
        if self.data.flags[Flag.UV]:
            self._parse_uv1(mesh, counts.vertices)

        # Texture coordinates (AO)
        if self.data.flags[Flag.UV2]:
            self._parse_uv2(mesh, counts.vertices)

        # Vertices normals
        if self.data.flags[Flag.NORMALS]:
            mesh.normals = self.io.normals(counts.vertices)

        # ? Not parsed
        # Vertices tangents
        if self.data.flags[Flag.TANGENTS]:
            mesh.tangents = self.io.tangents(counts.vertices)

        # ? Not parsed
        # Vertices rgba colors
        if self.data.flags[Flag.COLORS]:
            self.io.skip(counts.vertices * 4)

        # Vertices bones links
        if self.data.flags[Flag.SKELETON]:
            self._parse_links(mesh, counts.vertices, counts.max_influences)

        # Blend Shape Mapping
        if channel_ids is not None:
            mesh.blend_vertex_map = self.io.array(F.U16, counts.vertices)

        # Polygon faces
        mesh.polygons = self.io.polygons(counts.polygons, mesh.polygon_quads)

        # Blend Shape Deltas
        if channel_ids is not None:
            self._parse_blend_shapes(mesh, channel_ids)

        self.data.scene.meshes.append(mesh)

    def _parse_blend_shape_mapping(
        self,
        mesh: S.ModelMesh,
        counts: MeshCounts,
    ) -> np.ndarray | None:
        if self.data.version < 15.0:
            return None

        mesh.has_blend_shapes = self.io.value(F.BOOL)
        if not mesh.has_blend_shapes:
            return None

        counts.blend_shapes = self.io.value(F.U8)
        return self.io.array(F.I16, counts.blend_shapes)

    def _parse_blend_shapes(self, mesh: S.ModelMesh, channel_ids: np.ndarray):
        # # Unknown: Skip reference string
        self.io.string()

        count = self.io.value(F.U8)
        vertices = self.io.count(F.U16, Limit.VERTICES)
        names = [self.io.string() for _ in range(count)]

        if len(channel_ids) != count:
            raise BinaryStructureError(location=self.location, offset=self.io.tell())

        self.io.check(count * vertices, Limit.BLEND_DELTAS)
        deltas = self.io.blend_shapes(count, vertices, mesh.blend_vertex_map)

        for index, (name, delta, channel_id) in enumerate(zip(names, deltas, channel_ids)):
            # Omit undeformed basis target
            if index == 0 and not delta.any():
                continue

            shape = S.BlendShape(name, delta)
            mesh.blend_shapes.append(shape)
            self.ctx["BLEND_SHAPE_CHANNELS"].append((shape, int(channel_id)))

    def _parse_positions(self, mesh: S.ModelMesh, count: int):
        mesh.vertices = self.io.vertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=Units.POSITIONS,
            scale=self.data.scene.scale.position,
            count=count,
        )[:, :3]

    def _parse_uv1(self, mesh: S.ModelMesh, count: int):
        mesh.uv1 = self.io.vertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=Units.TEXTURES,
            scale=self.data.scene.scale.uv,
            count=count,
        )

    def _parse_uv2(self, mesh: S.ModelMesh, count: int):
        mesh.uv2 = self.io.vertex(
            fmt=F.I16,
            factor=Factor.I16,
            units=Units.TEXTURES,
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
            links = self.io.packed_links(count, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self.io.skip(count * 4)

    def _parse_plain_links(self, mesh: S.ModelMesh, count: int):
        if self.options.skeleton:
            links = self.io.plain_links(count, mesh.bones)
            mesh.links_ids, mesh.links_weights = links

        else:
            self.io.skip(count * 8)

    def _parse_skeleton(self):
        self.ctx["COUNT_BONES"] = self.io.value(F.U8)
        self.ctx["COUNT_CHANNELS"] = 0

        for index in range(self.ctx["COUNT_BONES"]):
            self._parse_bone(index)

        if self.data.version >= 15.0:
            self.ctx["COUNT_CHANNELS"] = self.io.value(F.U16)
            animation = self.data.scene.animation
            animation.morph_channels = [self.io.string() for _ in range(self.ctx["COUNT_CHANNELS"])]
            self._resolve_blend_shape_channels()

    def _resolve_blend_shape_channels(self):
        channels = self.data.scene.animation.morph_channels

        for shape, channel_id in self.ctx["BLEND_SHAPE_CHANNELS"]:
            if channel_id < 0:
                continue

            if channel_id >= len(channels):
                raise BinaryStructureError(location=self.location, offset=self.io.tell())

            shape.channel = channels[channel_id]

    def _parse_bone(self, index: int):
        bone = S.SkeletonBone()

        bone.id = index
        bone.name = self.io.string()

        # ? Bone is root if parent_id points to itself
        # ? self-reference would cause invalid recursion
        parent_id = self.io.value(F.U8)
        bone.parent_id = parent_id if parent_id != index else ModelDefaults.ROOT_BONE_ID

        bone.position, bone.tail = self.io.bone()

        self.data.scene.skeleton.bones.append(bone)

    def _parse_animation(self):
        self.ctx["COUNT_CLIPS"] = self.io.count(F.I32, Limit.CLIPS)

        for _ in range(self.ctx["COUNT_CLIPS"]):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self.io.string()
        clip.frames = self.io.count(F.U32, Limit.FRAMES)
        clip.rate = self.io.value(F.F32)

        channels = self.io.value(F.U16) if self.data.version >= 15.0 else 0
        transforms = clip.frames * self.ctx["COUNT_BONES"]
        self.io.check(transforms, Limit.TRANSFORMS)
        self.io.check(clip.frames * channels, Limit.WEIGHTS)

        rotations, translations, morph_weights = self.io.clip(
            clip.frames,
            self.ctx["COUNT_BONES"],
            channels,
            self.data.scene.scale.position,
        )

        clip.rotations = rotations
        clip.translations = translations
        clip.morph_weights = morph_weights

        self.data.scene.animation.clips.append(clip)
