import json
from copy import deepcopy
from typing import Any, Optional, TypeAlias

import numpy as np

from scfile.consts import FileSignature
from scfile.core import FileEncoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.models import AnimationClip, BlendShape, Flag, MorphWeights
from scfile.structures.models import transforms as T

from . import base
from .enums import BufferTarget, ComponentType


VERSION = 2

Node: TypeAlias = dict[str, Any]
BufferView: TypeAlias = dict[str, int]
Accessor: TypeAlias = dict[str, str | int]


class GlbEncoder(FileEncoder[ModelContent]):
    format = FileFormat.GLB
    signature = FileSignature.GLTF
    order = ByteOrder.LITTLE

    transforms = [T.unique_names, T.build_hierarchy, T.skeleton_to_local, T.animation_to_absolute]

    def serialize(self):
        self._add_header()
        self._create_gltf()
        self._add_json_chunk()
        self._add_binary_chunk()
        self._update_total_size()

    def _add_header(self):
        self._writeb(F.U32, VERSION)

        # Total Size Placeholder
        self.ctx["TOTAL_SIZE_POS"] = self.tell()
        self._writeb(F.U32, 0)

    def _update_total_size(self):
        self.seek(self.ctx["TOTAL_SIZE_POS"])
        self._writeb(F.U32, len(self.getvalue()))

    def _add_json_chunk(self):
        # Serialize gltf json
        gltf = json.dumps(self.ctx["GLTF"])
        gltf_bytes = gltf.encode()
        json_length = len(gltf_bytes)

        # Validate padding length
        padding_length = (4 - (json_length % 4)) % 4

        # Write json
        self._writeb(F.U32, json_length + padding_length)
        self.write(b"JSON")
        self.write(gltf_bytes)

        # Add padding if necessary
        if padding_length > 0:
            self.write(b"\x20" * padding_length)

    def _create_gltf(self):
        self.ctx["GLTF"] = deepcopy(base.GLTF)
        self.ctx["BUFFER_VIEW_OFFSET"] = 0

        # Create scene
        scene: Node = deepcopy(base.SCENE)
        self.ctx["GLTF"]["scenes"].append(scene)

        # Create skeleton keys
        if self._skeleton_presented:
            self.ctx["GLTF"]["skins"] = []

        if self._animation_presented:
            self.ctx["GLTF"]["animations"] = []

        # Create nodes
        self._create_nodes()
        self._count_nodes()

        # Write length in buffers
        self.ctx["GLTF"]["buffers"].append(deepcopy(base.BUFFER))
        self.ctx["GLTF"]["buffers"][0]["byteLength"] = self.ctx["BUFFER_VIEW_OFFSET"]

    def _create_nodes(self):
        self._create_meshes()

        if self._skeleton_presented:
            self._create_bones()
            self._create_bindmatrices()

        if self._animation_presented:
            self._create_animation()

    def _count_nodes(self):
        nodes = list(range(len(self.data.scene.meshes)))

        if self._skeleton_presented:
            nodes += self.ctx["ROOT_INDEXES"]

        self.ctx["GLTF"]["scenes"][0]["nodes"] = nodes

    def _accessor_index(self) -> int:
        return len(self.ctx["GLTF"]["accessors"])

    def _create_meshes(self):
        for index, mesh in enumerate(self.data.scene.meshes):
            primitive: Node = deepcopy(base.PRIMITIVE)
            skeleton_presented = self._skeleton_presented and mesh.max_influences > 0

            # XYZ Position
            primitive["attributes"]["POSITION"] = self._accessor_index()
            self._create_bufferview(byte_length=len(mesh.vertices) * 3 * 4)
            self._create_accessor(len(mesh.vertices), "VEC3", array=mesh.vertices)

            # Blend Shapes
            if mesh.blend_shapes:
                primitive["targets"] = []

                for shape in mesh.blend_shapes:
                    primitive["targets"].append({"POSITION": self._accessor_index()})
                    self._create_bufferview(byte_length=len(mesh.vertices) * 3 * 4)
                    self._create_accessor(len(mesh.vertices), "VEC3", array=shape.deltas)

            # UV Texture
            if self.data.flags[Flag.UV] and mesh.uv1.size:
                primitive["attributes"]["TEXCOORD_0"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 2 * 4)
                self._create_accessor(len(mesh.vertices), "VEC2")

            # UV Texture (2)
            if self.data.flags[Flag.UV2] and mesh.uv2.size:
                primitive["attributes"]["TEXCOORD_1"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 2 * 4)
                self._create_accessor(len(mesh.vertices), "VEC2")

            # XYZ Normals
            if self.data.flags[Flag.NORMALS] and mesh.normals.size:
                primitive["attributes"]["NORMAL"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 3 * 4)
                self._create_accessor(len(mesh.vertices), "VEC3")

            # XYZW Tangents
            if self.data.flags[Flag.TANGENTS] and mesh.tangents.size:
                primitive["attributes"]["TANGENT"] = self._accessor_index()
                self._create_bufferview(byte_length=len(mesh.vertices) * 4 * 4)
                self._create_accessor(len(mesh.vertices), "VEC4")

            # Bone Links
            if skeleton_presented:
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

            if skeleton_presented:
                node["skin"] = self.ctx["MESH_SKINS"][index] if "MESH_SKINS" in self.ctx else 0

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)
            gltf_mesh: Node = dict(name=mesh.name, primitives=[primitive])

            if mesh.blend_shapes:
                gltf_mesh["weights"] = [0.0] * len(mesh.blend_shapes)
                gltf_mesh["extras"] = {"targetNames": [shape.name for shape in mesh.blend_shapes]}

            self.ctx["GLTF"]["meshes"].append(gltf_mesh)
            self.ctx["GLTF"]["materials"].append(dict(name=mesh.material, pbrMetallicRoughness=base.PBR))

    def _create_bones(self):
        self.ctx["BONE_INDEXES"] = []
        self.ctx["ROOT_INDEXES"] = []

        node_index_offset = len(self.data.scene.meshes)

        for index, bone in enumerate(self.data.scene.skeleton.bones, start=node_index_offset):
            node: Node = dict(
                name=bone.name,
                translation=bone.position.tolist(),
                rotation=bone.quaternion.tolist(),
            )

            self.ctx["BONE_INDEXES"].append(index)

            if bone.is_root:
                self.ctx["ROOT_INDEXES"].append(index)

            if bone.children:
                node["children"] = [node_index_offset + child.id for child in bone.children]

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)

    def _create_bindmatrices(self):
        skins = self.ctx.get("SKINS", (None,))

        for _ in skins:
            self.ctx["GLTF"]["skins"].append(
                dict(
                    name="Armature",
                    inverseBindMatrices=self._accessor_index(),
                    joints=self.ctx["BONE_INDEXES"],
                )
            )
            count = len(self.data.scene.skeleton.bones)
            self._create_bufferview(byte_length=count * 16 * 4, target=None)
            self._create_accessor(count, "MAT4", ComponentType.FLOAT)

    def _create_animation(self):
        for clip in self.data.scene.animation.clips:
            morph_targets = self._morph_animation_targets(clip)
            bone_animation = self._bone_animation_presented(clip)
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
                for node_index in self.ctx["BONE_INDEXES"]:
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

            self.ctx["GLTF"]["animations"].append(dict(name=clip.name, samplers=samplers, channels=channels))

    def _morph_animation_targets(self, clip: AnimationClip) -> list[tuple[int, MorphWeights]]:
        if not clip.morph_weights.size:
            return []

        channels = {name: index for index, name in enumerate(self.data.scene.animation.morph_channels)}
        targets = []

        for node_index, mesh in enumerate(self.data.scene.meshes):
            weights = self._morph_weights(clip, mesh.blend_shapes, channels)
            if weights is None:
                continue

            targets.append((node_index, weights))

        return targets

    @staticmethod
    def _morph_weights(
        clip: AnimationClip,
        shapes: list[BlendShape],
        channels: dict[str, int],
    ) -> MorphWeights | None:
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
        target: Optional[BufferTarget] = BufferTarget.ARRAY_BUFFER,
    ):
        view: BufferView = dict(
            buffer=0,
            byteLength=byte_length,
            byteOffset=self.ctx["BUFFER_VIEW_OFFSET"],
        )

        if target:
            view["target"] = target.value

        self.ctx["GLTF"]["bufferViews"].append(view)
        self.ctx["BUFFER_VIEW_OFFSET"] += byte_length

    def _create_accessor(
        self,
        count: int,
        accessor_type: str,
        component_type: ComponentType = ComponentType.FLOAT,
        array: Optional[np.ndarray] = None,
    ):
        buffer_view_idx = len(self.ctx["GLTF"]["bufferViews"]) - 1
        accessor: Accessor = dict(
            bufferView=buffer_view_idx,
            count=count,
            componentType=component_type.value,
            type=accessor_type,
        )

        if array is not None:
            accessor["min"] = np.min(array, axis=0).tolist()
            accessor["max"] = np.max(array, axis=0).tolist()

        self.ctx["GLTF"]["accessors"].append(accessor)

    def _add_binary_chunk(self):
        self._add_bin_size()
        self.ctx["BIN_START"] = self.tell()

        self._add_meshes()

        if self._skeleton_presented:
            # Animated model sources may require separate bind poses
            if "SKINS" in self.ctx:
                for bindpose in self.ctx["SKINS"]:
                    self.write(bindpose.transpose(0, 2, 1).tobytes())
            else:
                bindpose = self.data.scene.skeleton.inverse_bind_matrices(transpose=True)
                self.write(bindpose.tobytes())

        if self._animation_presented:
            self._add_animation()

        self.ctx["BIN_END"] = self.tell()
        self._update_bin_size()

    def _add_bin_size(self):
        # BIN Size Placeholder
        self.ctx["BIN_SIZE_POS"] = self.tell()
        self._writeb(F.U32, 0)
        self.write(b"BIN\0")

    def _update_bin_size(self):
        size = self.ctx["BIN_END"] - self.ctx["BIN_START"]
        self.seek(self.ctx["BIN_SIZE_POS"])
        self._writeb(F.U32, size)

    def _add_meshes(self):
        for mesh in self.data.scene.meshes:
            skeleton_presented = self._skeleton_presented and mesh.max_influences > 0

            # XYZ Position
            self.write(mesh.vertices.tobytes())

            # Blend Shapes
            for shape in mesh.blend_shapes:
                self.write(shape.deltas.tobytes())

            # UV Texture
            if self.data.flags[Flag.UV] and mesh.uv1.size:
                self.write(mesh.uv1.tobytes())

            # UV Texture (2)
            if self.data.flags[Flag.UV2] and mesh.uv2.size:
                self.write(mesh.uv2.tobytes())

            # XYZ Normals
            if self.data.flags[Flag.NORMALS] and mesh.normals.size:
                self.write(mesh.normals.tobytes())

            # XYZW Tangents
            if self.data.flags[Flag.TANGENTS] and mesh.tangents.size:
                self.write(mesh.tangents.tobytes())

            # Bone Links
            if skeleton_presented:
                # Joint Indices
                self.write(mesh.links_ids.tobytes())

                # Joint Weights
                self.write(mesh.links_weights.tobytes())

            # ABC Polygons
            self.write(mesh.polygons.flatten().astype(F.U32).tobytes())

    def _add_animation(self):
        for clip in self.data.scene.animation.clips:
            morph_targets = self._morph_animation_targets(clip)
            bone_animation = self._bone_animation_presented(clip)
            if not bone_animation and not morph_targets:
                continue

            self.write(clip.times.tobytes())

            if bone_animation:
                for bone in self.data.scene.skeleton.bones:
                    self.write(clip.translations[:, bone.id, :].tobytes())
                    self.write(clip.rotations[:, bone.id, :].tobytes())

            for _, weights in morph_targets:
                self.write(weights.tobytes())
