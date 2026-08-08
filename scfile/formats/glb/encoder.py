import json
from copy import deepcopy
from typing import Any, override

import numpy as np

from scfile.consts import FormatSignature
from scfile.core import ModelEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import transforms as T

from . import base
from .enums import BufferTarget, ComponentType


VERSION = 2

type Node = dict[str, Any]
type BufferView = dict[str, int]
type Accessor = dict[str, str | int]


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
        self._create_gltf()
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
        gltf = json.dumps(self._ctx["GLTF"])
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

    def _create_gltf(self):
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
        self._create_nodes()
        self._count_nodes()

        # Write length in buffers
        self._ctx["GLTF"]["buffers"].append(deepcopy(base.BUFFER))
        self._ctx["GLTF"]["buffers"][0]["byteLength"] = self._ctx["BUFFER_VIEW_OFFSET"]

    def _create_nodes(self):
        self._create_meshes()

        if self.includes(S.Feature.SKELETON):
            self._create_bones()
            self._create_bindmatrices()

        if self.includes(S.Feature.ANIMATION):
            self._create_animation()

    def _count_nodes(self):
        nodes = list(range(len(self.data.scene.meshes)))

        if self.includes(S.Feature.SKELETON):
            nodes += self._ctx["ROOT_INDEXES"]

        self._ctx["GLTF"]["scenes"][0]["nodes"] = nodes

    def _accessor_index(self) -> int:
        return len(self._ctx["GLTF"]["accessors"])

    def _create_meshes(self):
        for index, mesh in enumerate(self.data.scene.meshes):
            primitive: Node = deepcopy(base.PRIMITIVE)
            has_skin = self.includes(S.Feature.SKELETON) and mesh.max_influences > 0

            # XYZ Position
            primitive["attributes"]["POSITION"] = self._accessor_index()
            self._create_bufferview(byte_length=len(mesh.vertices) * 3 * 4)
            self._create_accessor(len(mesh.vertices), "VEC3", array=mesh.vertices)

            # Blend Shapes
            if self.includes(S.Feature.BLEND_SHAPES) and mesh.blend_shapes:
                primitive["targets"] = []

                for shape in mesh.blend_shapes:
                    primitive["targets"].append({"POSITION": self._accessor_index()})
                    self._create_bufferview(byte_length=len(mesh.vertices) * 3 * 4)
                    self._create_accessor(len(mesh.vertices), "VEC3", array=shape.deltas)

            # UV Texture
            if self.includes(S.Feature.UV) and mesh.uv1.size:
                primitive["attributes"]["TEXCOORD_0"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 2 * 4)
                self._create_accessor(len(mesh.vertices), "VEC2")

            # UV Texture (2)
            if self.includes(S.Feature.UV2) and mesh.uv2.size:
                primitive["attributes"]["TEXCOORD_1"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 2 * 4)
                self._create_accessor(len(mesh.vertices), "VEC2")

            # XYZ Normals
            if self.includes(S.Feature.NORMALS) and mesh.normals.size:
                primitive["attributes"]["NORMAL"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 3 * 4)
                self._create_accessor(len(mesh.vertices), "VEC3")

            # XYZW Tangents
            if self.includes(S.Feature.TANGENTS) and mesh.tangents.size:
                primitive["attributes"]["TANGENT"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 4 * 4)
                self._create_accessor(len(mesh.vertices), "VEC4")

            # Bone Links
            if has_skin:
                # Joint Indices
                primitive["attributes"]["JOINTS_0"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 4 * 1)
                self._create_accessor(len(mesh.vertices), "VEC4", ComponentType.UBYTE)

                # Joint Weights
                primitive["attributes"]["WEIGHTS_0"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 4 * 4)
                self._create_accessor(len(mesh.vertices), "VEC4", ComponentType.FLOAT)

            # ABC Polygons
            primitive["indices"] = self._accessor_index()
            self._create_bufferview(byte_length=len(mesh.polygons) * 4 * 3, target=BufferTarget.ELEMENT_ARRAY_BUFFER)
            self._create_accessor(len(mesh.polygons) * 3, "SCALAR", ComponentType.UINT32)

            # Create nodes
            primitive["material"] = index
            node: Node = {"name": mesh.name, "mesh": index}

            if has_skin:
                node["skin"] = mesh.skin if mesh.skin is not None else 0

            # Add to GLTF
            self._ctx["GLTF"]["nodes"].append(node)
            gltf_mesh: Node = dict(name=mesh.name, primitives=[primitive])

            if self.includes(S.Feature.BLEND_SHAPES) and mesh.blend_shapes:
                gltf_mesh["weights"] = [0.0] * len(mesh.blend_shapes)
                gltf_mesh["extras"] = {"targetNames": [shape.name for shape in mesh.blend_shapes]}

            self._ctx["GLTF"]["meshes"].append(gltf_mesh)
            self._ctx["GLTF"]["materials"].append(dict(name=mesh.material, pbrMetallicRoughness=base.PBR))

    def _create_bones(self):
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

    def _create_bindmatrices(self):
        skins = self.data.scene.skins or (None,)

        for _ in skins:
            self._ctx["GLTF"]["skins"].append(
                dict(
                    name="Armature",
                    inverseBindMatrices=self._accessor_index(),
                    joints=self._ctx["BONE_INDEXES"],
                )
            )
            count = len(self.data.scene.skeleton.bones)
            self._create_bufferview(byte_length=count * 16 * 4, target=None)
            self._create_accessor(count, "MAT4", ComponentType.FLOAT)

    def _create_animation(self):
        for clip in self.data.scene.animation.clips:
            morph_targets = self._morph_animation_targets(clip)
            bone_animation = (
                self.includes(S.Feature.BONE_ANIMATION) and bool(clip.translations.size) and bool(clip.rotations.size)
            )
            if not bone_animation and not morph_targets:
                continue

            times = clip.times
            time_idx = self._accessor_index()
            self._create_bufferview(byte_length=clip.frames * 4, target=None)
            self._create_accessor(clip.frames, "SCALAR", ComponentType.FLOAT, array=times.reshape(-1, 1))

            sampler_idx = 0
            samplers = []
            channels = []

            if bone_animation:
                for node_index in self._ctx["BONE_INDEXES"]:
                    translation_idx = self._accessor_index()
                    self._create_bufferview(byte_length=clip.frames * 3 * 4, target=None)
                    self._create_accessor(clip.frames, "VEC3", ComponentType.FLOAT)

                    rotation_idx = self._accessor_index()
                    self._create_bufferview(byte_length=clip.frames * 4 * 4, target=None)
                    self._create_accessor(clip.frames, "VEC4", ComponentType.FLOAT)

                    samplers.extend(
                        [
                            dict(input=time_idx, output=translation_idx, interpolation="LINEAR"),
                            dict(input=time_idx, output=rotation_idx, interpolation="LINEAR"),
                        ]
                    )
                    channels.extend(
                        [
                            dict(sampler=sampler_idx, target=dict(node=node_index, path="translation")),
                            dict(sampler=sampler_idx + 1, target=dict(node=node_index, path="rotation")),
                        ]
                    )
                    sampler_idx += 2

            for node_index, weights in morph_targets:
                weights_idx = self._accessor_index()
                self._create_bufferview(byte_length=weights.nbytes, target=None)
                self._create_accessor(weights.size, "SCALAR", ComponentType.FLOAT)

                samplers.append(dict(input=time_idx, output=weights_idx, interpolation="LINEAR"))
                channels.append(dict(sampler=sampler_idx, target=dict(node=node_index, path="weights")))
                sampler_idx += 1

            self._ctx["GLTF"]["animations"].append(dict(name=clip.name, samplers=samplers, channels=channels))

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

    def _create_bufferview(
        self,
        byte_length: int,
        target: BufferTarget | None = BufferTarget.ARRAY_BUFFER,
    ):
        view: BufferView = dict(
            buffer=0,
            byteLength=byte_length,
            byteOffset=self._ctx["BUFFER_VIEW_OFFSET"],
        )

        if target:
            view["target"] = target.value

        self._ctx["GLTF"]["bufferViews"].append(view)
        self._ctx["BUFFER_VIEW_OFFSET"] += byte_length

    def _create_accessor(
        self,
        count: int,
        accessor_type: str,
        component_type: ComponentType = ComponentType.FLOAT,
        array: np.ndarray | None = None,
    ):
        buffer_view_idx = len(self._ctx["GLTF"]["bufferViews"]) - 1
        accessor: Accessor = dict(
            bufferView=buffer_view_idx,
            count=count,
            componentType=component_type.value,
            type=accessor_type,
        )

        if array is not None:
            accessor["min"] = np.min(array, axis=0).tolist()
            accessor["max"] = np.max(array, axis=0).tolist()

        self._ctx["GLTF"]["accessors"].append(accessor)

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
            has_skin = self.includes(S.Feature.SKELETON) and mesh.max_influences > 0

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
            if has_skin:
                # Joint Indices
                self.io.write(mesh.links_ids.tobytes())

                # Joint Weights
                self.io.write(mesh.links_weights.tobytes())

            # ABC Polygons
            self.io.write(mesh.polygons.flatten().astype(F.U32).tobytes())

    def _add_animation(self):
        for clip in self.data.scene.animation.clips:
            morph_targets = self._morph_animation_targets(clip)
            bone_animation = (
                self.includes(S.Feature.BONE_ANIMATION) and bool(clip.translations.size) and bool(clip.rotations.size)
            )
            if not bone_animation and not morph_targets:
                continue

            self.io.write(clip.times.tobytes())

            if bone_animation:
                for bone in self.data.scene.skeleton.bones:
                    self.io.write(clip.translations[:, bone.id, :].tobytes())
                    self.io.write(clip.rotations[:, bone.id, :].tobytes())

            for _, weights in morph_targets:
                self.io.write(weights.tobytes())
