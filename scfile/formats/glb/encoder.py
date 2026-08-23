import json
from copy import deepcopy
from typing import Any, override

import numpy as np

from scfile.consts import FormatSignature
from scfile.content import models as S
from scfile.content.models import transforms as T
from scfile.core import ModelEncoder
from scfile.enums import ByteOrder, F, FileFormat

from . import base
from .enums import BufferTarget, ComponentType


VERSION = 2

type Node = dict[str, Any]
type BufferView = dict[str, int]
type Accessor = dict[str, str | int]
type ClipChannel = tuple[str, int, int, np.ndarray]
type ClipChannels = tuple[tuple[np.ndarray, ...], tuple[ClipChannel, ...]]


class GlbEncoder(ModelEncoder):
    format = FileFormat.GLB
    signature = FormatSignature.GLTF
    order = ByteOrder.LITTLE

    features = (
        S.Feature.UV,
        S.Feature.UV2,
        S.Feature.NORMALS,
        S.Feature.TANGENTS,
        S.Feature.SKELETON,
        S.Feature.BLEND_SHAPES,
        S.Feature.BONE_ANIMATION,
        S.Feature.MORPH_ANIMATION,
    )
    transforms = T.scene_transforms(
        T.unique_names,
        T.skeleton_to_local,
        T.animation_to_absolute,
    )

    @override
    def _serialize(self):
        self._add_header()
        self._build_document()
        self._add_json_chunk()
        self._add_binary_chunk()
        self._update_total_size()

    def _add_header(self):
        self.io.value(F.U32, VERSION)

        # Total Size Placeholder
        self._ctx["TOTAL_SIZE_POS"] = self.io.tell()
        self.io.value(F.U32, 0)

    def _update_total_size(self):
        self.io.seek(self._ctx["TOTAL_SIZE_POS"])
        self.io.value(F.U32, self.io.size())

    def _add_json_chunk(self):
        # Serialize gltf json
        gltf = json.dumps(self._ctx["GLTF"], ensure_ascii=False, separators=(",", ":"))
        gltf_bytes = gltf.encode()
        json_length = len(gltf_bytes)

        # Validate padding length
        padding_length = (4 - (json_length % 4)) % 4

        # Write json
        self.io.value(F.U32, json_length + padding_length)
        self.io.write(b"JSON")
        self.io.write(gltf_bytes)

        # Add padding if necessary
        if padding_length > 0:
            self.io.write(b"\x20" * padding_length)

    def _build_document(self):
        self._ctx["GLTF"] = deepcopy(base.GLTF)
        self._ctx["BUFFER_VIEW_OFFSET"] = 0

        # Create scene
        scene: Node = deepcopy(base.SCENE)
        self._ctx["GLTF"]["scenes"].append(scene)

        # Create skeleton keys
        if self.includes(S.Feature.SKELETON):
            self._ctx["GLTF"]["skins"] = []

        if self.includes(S.Feature.ANIMATION):
            self._ctx["GLTF"]["animations"] = []

        # Create nodes
        self._build_nodes()
        self._set_scene_nodes()

        # Write length in buffers
        self._ctx["GLTF"]["buffers"].append(deepcopy(base.BUFFER))
        self._ctx["GLTF"]["buffers"][0]["byteLength"] = self._ctx["BUFFER_VIEW_OFFSET"]

    def _build_nodes(self):
        self._build_meshes()

        if self.includes(S.Feature.SKELETON):
            self._build_bones()
            self._build_skins()

        if self.includes(S.Feature.ANIMATION):
            self._build_animation()

    def _set_scene_nodes(self):
        nodes = list(range(len(self.data.scene.meshes)))

        if self.includes(S.Feature.SKELETON):
            nodes += self._ctx["ROOT_INDEXES"]

        self._ctx["GLTF"]["scenes"][0]["nodes"] = nodes

    def _build_meshes(self):
        for index, mesh in enumerate(self.data.scene.meshes):
            primitive: Node = deepcopy(base.PRIMITIVE)
            attributes = primitive["attributes"]
            use_skin = self.includes(S.Feature.SKELETON) and mesh.max_influences > 0

            # XYZ Position
            attributes["POSITION"] = self._create_accessor(mesh.vertices, "VEC3", bounds=True)

            # Blend Shapes
            if self.includes(S.Feature.BLEND_SHAPES) and mesh.blend_shapes:
                primitive["targets"] = []

                for shape in mesh.blend_shapes:
                    primitive["targets"].append({"POSITION": self._create_accessor(shape.deltas, "VEC3", bounds=True)})

            # UV Texture
            if self.includes(S.Feature.UV) and mesh.uv1.size:
                attributes["TEXCOORD_0"] = self._create_accessor(mesh.uv1, "VEC2")

            # UV Texture (2)
            if self.includes(S.Feature.UV2) and mesh.uv2.size:
                attributes["TEXCOORD_1"] = self._create_accessor(mesh.uv2, "VEC2")

            # XYZ Normals
            if self.includes(S.Feature.NORMALS) and mesh.normals.size:
                attributes["NORMAL"] = self._create_accessor(mesh.normals, "VEC3")

            # XYZW Tangents
            if self.includes(S.Feature.TANGENTS) and mesh.tangents.size:
                attributes["TANGENT"] = self._create_accessor(mesh.tangents, "VEC4")

            # Bone Links
            if use_skin:
                # Joint Indices
                attributes["JOINTS_0"] = self._create_accessor(mesh.links_ids, "VEC4", ComponentType.UBYTE)
                # Joint Weights
                attributes["WEIGHTS_0"] = self._create_accessor(mesh.links_weights, "VEC4")

            # ABC Polygons
            primitive["indices"] = self._create_accessor(
                mesh.polygons,
                "SCALAR",
                ComponentType.UINT32,
                target=BufferTarget.ELEMENT_ARRAY_BUFFER,
                count=mesh.polygons.size,
            )

            # Create nodes
            primitive["material"] = index
            node: Node = {"name": mesh.name, "mesh": index}

            if use_skin:
                node["skin"] = mesh.skin if mesh.skin is not None else 0

            # Add to GLTF
            self._ctx["GLTF"]["nodes"].append(node)
            gltf_mesh: Node = dict(name=mesh.name, primitives=[primitive])

            if self.includes(S.Feature.BLEND_SHAPES) and mesh.blend_shapes:
                gltf_mesh["weights"] = [0.0] * len(mesh.blend_shapes)
                gltf_mesh["extras"] = {"targetNames": [shape.name for shape in mesh.blend_shapes]}

            self._ctx["GLTF"]["meshes"].append(gltf_mesh)
            self._ctx["GLTF"]["materials"].append(dict(name=mesh.material, pbrMetallicRoughness=base.PBR))

    def _build_bones(self):
        self._ctx["BONE_INDEXES"] = []
        self._ctx["ROOT_INDEXES"] = []

        node_index_offset = len(self.data.scene.meshes)
        bones = self.data.scene.skeleton.bones
        children: list[list[int]] = [[] for _ in bones]

        for bone in bones:
            if not bone.is_root:
                children[bone.parent_id].append(node_index_offset + bone.id)

        for index, bone in enumerate(bones, start=node_index_offset):
            node: Node = dict(
                name=bone.name,
                translation=bone.position.tolist(),
                rotation=bone.quaternion.tolist(),
            )

            self._ctx["BONE_INDEXES"].append(index)

            if bone.is_root:
                self._ctx["ROOT_INDEXES"].append(index)

            if children[bone.id]:
                node["children"] = children[bone.id]

            # Add to GLTF
            self._ctx["GLTF"]["nodes"].append(node)

    def _build_skins(self):
        skins = self.data.scene.skins or (None,)

        for skin in skins:
            matrices = (
                skin.bind_matrices.transpose(0, 2, 1)
                if skin is not None
                else T.inverse_bind_matrices(self.data.scene.skeleton, transpose=True)
            )
            self._ctx["GLTF"]["skins"].append(
                dict(
                    name="Armature",
                    inverseBindMatrices=self._create_accessor(matrices, "MAT4", target=None),
                    joints=self._ctx["BONE_INDEXES"],
                )
            )

    def _build_animation(self):
        for clip in self.data.scene.animation.clips:
            channels = self._clip_channels(clip)
            if channels is None:
                continue

            times, tracks = channels
            time_indexes = [
                self._create_accessor(time_values.reshape(-1, 1), "SCALAR", target=None, bounds=True)
                for time_values in times
            ]

            sampler_idx = 0
            samplers = []
            animation_channels = []

            for path, node_index, time_index, values in tracks:
                accessor_type = "SCALAR" if path == "weights" else "VEC3" if path == "translation" else "VEC4"
                count = values.size if path == "weights" else None
                output_index = self._create_accessor(values, accessor_type, target=None, count=count)

                samplers.append(dict(input=time_indexes[time_index], output=output_index, interpolation="LINEAR"))
                animation_channels.append(dict(sampler=sampler_idx, target=dict(node=node_index, path=path)))
                sampler_idx += 1

            self._ctx["GLTF"]["animations"].append(dict(name=clip.name, samplers=samplers, channels=animation_channels))

    def _clip_channels(self, clip: S.AnimationClip) -> ClipChannels | None:
        morph_targets = self._morph_animation_targets(clip)
        bone_animation = (
            self.includes(S.Feature.BONE_ANIMATION) and bool(clip.translations.size) and bool(clip.rotations.size)
        )
        if not bone_animation and not morph_targets:
            return None

        times = [clip.times]
        tracks: list[ClipChannel] = []

        if bone_animation:
            bone_tracks = []
            for bone, node_index in zip(self.data.scene.skeleton.bones, self._ctx["BONE_INDEXES"]):
                bone_tracks.extend(
                    (
                        ("translation", node_index, clip.translations[:, bone.id, :]),
                        ("rotation", node_index, clip.rotations[:, bone.id, :]),
                    )
                )

            static = [_constant_channel(values) for _, _, values in bone_tracks]
            compact = not self.options.raw_clips and any(static) and not all(static)
            if compact:
                times.append(times[0][:1])

            tracks.extend(
                (
                    path,
                    node_index,
                    1 if compact and is_static else 0,
                    values[:1] if compact and is_static else values,
                )
                for (path, node_index, values), is_static in zip(bone_tracks, static)
            )

        tracks.extend(("weights", node_index, 0, weights) for node_index, weights in morph_targets)
        return tuple(times), tuple(tracks)

    def _morph_animation_targets(self, clip: S.AnimationClip) -> list[tuple[int, S.MorphWeights]]:
        if not self.includes(S.Feature.MORPH_ANIMATION) or not clip.morph_weights.size:
            return []

        channels = {name: index for index, name in enumerate(self.data.scene.animation.morph_channels)}
        targets = []

        for node_index, mesh in enumerate(self.data.scene.meshes):
            weights = self._morph_weights(clip, mesh.blend_shapes, channels)
            if weights is None:
                continue

            targets.append((node_index, weights))

        return targets

    def _morph_weights(
        self,
        clip: S.AnimationClip,
        shapes: list[S.BlendShape],
        channels: dict[str, int],
    ) -> S.MorphWeights | None:
        weights = np.zeros((clip.frames, len(shapes)), dtype=np.float32)
        mapped = False

        for target_index, shape in enumerate(shapes):
            if shape.channel is None:
                continue

            channel_index = channels.get(shape.channel)
            if channel_index is None:
                continue

            weights[:, target_index] = clip.morph_weights[:, channel_index]
            mapped = True

        return weights if mapped else None

    def _create_accessor(
        self,
        values: np.ndarray,
        accessor_type: str,
        component_type: ComponentType = ComponentType.FLOAT,
        *,
        target: BufferTarget | None = BufferTarget.ARRAY_BUFFER,
        count: int | None = None,
        bounds: bool = False,
    ) -> int:
        accessor_index = len(self._ctx["GLTF"]["accessors"])
        view: BufferView = dict(
            buffer=0,
            byteLength=values.nbytes,
            byteOffset=self._ctx["BUFFER_VIEW_OFFSET"],
        )

        if target:
            view["target"] = target.value

        self._ctx["GLTF"]["bufferViews"].append(view)
        self._ctx["BUFFER_VIEW_OFFSET"] += values.nbytes

        accessor: Accessor = dict(
            bufferView=len(self._ctx["GLTF"]["bufferViews"]) - 1,
            count=count if count is not None else len(values),
            componentType=component_type.value,
            type=accessor_type,
        )

        if bounds:
            accessor["min"] = np.min(values, axis=0).tolist()
            accessor["max"] = np.max(values, axis=0).tolist()

        self._ctx["GLTF"]["accessors"].append(accessor)
        return accessor_index

    def _add_binary_chunk(self):
        self._add_bin_size()
        self._ctx["BIN_START"] = self.io.tell()

        self._add_meshes()

        if self.includes(S.Feature.SKELETON):
            if self.data.scene.skins:
                for skin in self.data.scene.skins:
                    self.io.write(skin.bind_matrices.transpose(0, 2, 1).tobytes())
            else:
                bindpose = T.inverse_bind_matrices(self.data.scene.skeleton, transpose=True)
                self.io.write(bindpose.tobytes())

        if self.includes(S.Feature.ANIMATION):
            self._add_animation()

        self._ctx["BIN_END"] = self.io.tell()
        self._update_bin_size()

    def _add_bin_size(self):
        # BIN Size Placeholder
        self._ctx["BIN_SIZE_POS"] = self.io.tell()
        self.io.value(F.U32, 0)
        self.io.write(b"BIN\0")

    def _update_bin_size(self):
        size = self._ctx["BIN_END"] - self._ctx["BIN_START"]
        self.io.seek(self._ctx["BIN_SIZE_POS"])
        self.io.value(F.U32, size)

    def _add_meshes(self):
        for mesh in self.data.scene.meshes:
            use_skin = self.includes(S.Feature.SKELETON) and mesh.max_influences > 0

            # XYZ Position
            self.io.write(mesh.vertices.tobytes())

            # Blend Shapes
            if self.includes(S.Feature.BLEND_SHAPES) and mesh.blend_shapes:
                for shape in mesh.blend_shapes:
                    self.io.write(shape.deltas.tobytes())

            # UV Texture
            if self.includes(S.Feature.UV) and mesh.uv1.size:
                self.io.write(mesh.uv1.tobytes())

            # UV Texture (2)
            if self.includes(S.Feature.UV2) and mesh.uv2.size:
                self.io.write(mesh.uv2.tobytes())

            # XYZ Normals
            if self.includes(S.Feature.NORMALS) and mesh.normals.size:
                self.io.write(mesh.normals.tobytes())

            # XYZW Tangents
            if self.includes(S.Feature.TANGENTS) and mesh.tangents.size:
                self.io.write(mesh.tangents.tobytes())

            # Bone Links
            if use_skin:
                # Joint Indices
                self.io.write(mesh.links_ids.tobytes())

                # Joint Weights
                self.io.write(mesh.links_weights.tobytes())

            # ABC Polygons
            self.io.write(mesh.polygons.flatten().astype(F.U32).tobytes())

    def _add_animation(self):
        for clip in self.data.scene.animation.clips:
            channels = self._clip_channels(clip)
            if channels is None:
                continue

            times, tracks = channels
            for values in times:
                self.io.write(values.tobytes())

            for _, _, _, values in tracks:
                self.io.write(values.tobytes())


def _constant_channel(values: np.ndarray) -> bool:
    return len(values) < 2 or np.array_equal(values[1:], values[:-1])
