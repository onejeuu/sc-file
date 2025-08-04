import json
from copy import deepcopy
from typing import Any, Optional, TypeAlias

import numpy as np

from scfile.consts import FileSignature
from scfile.core import FileEncoder, ModelContent
from scfile.enums import F, FileFormat
from scfile.structures.flags import Flag

from . import base
from .enums import BufferTarget, ComponentType


VERSION = 2

Node: TypeAlias = dict[str, Any]
BufferView: TypeAlias = dict[str, int]
Accessor: TypeAlias = dict[str, str | int]


class GlbEncoder(FileEncoder[ModelContent]):
    format = FileFormat.GLB
    signature = FileSignature.GLTF

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self._skeleton_presented:
            self.data.scene.skeleton.convert_to_local()
            self.data.scene.skeleton.build_hierarchy()

        if self._animation_presented:
            self.data.scene.animation.convert_to_local(self.data.scene.skeleton)

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
            self._create_bindmatrix()

        if self._animation_presented:
            self._create_animation()

    def _count_nodes(self):
        nodes = list(range(self.data.scene.count.meshes))

        if self._skeleton_presented:
            nodes += self.ctx["ROOT_INDEXES"]

        self.ctx["GLTF"]["scenes"][0]["nodes"] = nodes

    def _accessor_index(self) -> int:
        return len(self.ctx["GLTF"]["accessors"])

    def _create_meshes(self):
        for index, mesh in enumerate(self.data.scene.meshes):
            primitive: Node = deepcopy(base.PRIMITIVE)

            # XYZ Position
            primitive["attributes"]["POSITION"] = self._accessor_index()
            self._create_bufferview(byte_length=mesh.count.vertices * 3 * 4)
            self._create_accessor(mesh.count.vertices, "VEC3", array=mesh.positions)

            # UV Texture
            if self.data.flags[Flag.UV]:
                primitive["attributes"]["TEXCOORD_0"] = self._accessor_index()
                self._create_bufferview(byte_length=mesh.count.vertices * 2 * 4)
                self._create_accessor(mesh.count.vertices, "VEC2")

            # XYZ Normals
            if self.data.flags[Flag.NORMALS]:
                primitive["attributes"]["NORMAL"] = self._accessor_index()
                self._create_bufferview(byte_length=mesh.count.vertices * 3 * 4)
                self._create_accessor(mesh.count.vertices, "VEC3")

            # Bone Links
            if self._skeleton_presented and mesh.count.links > 0:
                # Joint Indices
                primitive["attributes"]["JOINTS_0"] = self._accessor_index()
                self._create_bufferview(byte_length=mesh.count.vertices * 4 * 1)
                self._create_accessor(mesh.count.vertices, "VEC4", ComponentType.UBYTE)

                # Joint Weights
                primitive["attributes"]["WEIGHTS_0"] = self._accessor_index()
                self._create_bufferview(byte_length=mesh.count.vertices * 4 * 4)
                self._create_accessor(mesh.count.vertices, "VEC4", ComponentType.FLOAT)

            # ABC Polygons
            primitive["indices"] = self._accessor_index()
            self._create_bufferview(byte_length=mesh.count.polygons * 4 * 3, target=BufferTarget.ELEMENT_ARRAY_BUFFER)
            self._create_accessor(mesh.count.polygons * 3, "SCALAR", ComponentType.UINT32)

            # Create nodes
            primitive["material"] = index
            node: Node = {"name": mesh.name, "mesh": index}

            if self._skeleton_presented and mesh.count.links > 0:
                node["skin"] = 0

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)
            self.ctx["GLTF"]["meshes"].append(dict(name=mesh.name, primitives=[primitive]))
            self.ctx["GLTF"]["materials"].append(dict(name=mesh.material, pbrMetallicRoughness=base.PBR))

    def _create_bones(self):
        self.ctx["BONE_INDEXES"] = []
        self.ctx["ROOT_INDEXES"] = []

        node_index_offset = self.data.scene.count.meshes

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

    def _create_bindmatrix(self):
        self.ctx["GLTF"]["skins"].append(
            dict(
                name="Armature",
                inverseBindMatrices=self._accessor_index(),
                joints=self.ctx["BONE_INDEXES"],
            )
        )
        self._create_bufferview(byte_length=self.data.scene.count.bones * 16 * 4, target=None)
        self._create_accessor(self.data.scene.count.bones, "MAT4", ComponentType.FLOAT)

    def _create_animation(self):
        for clip in self.data.scene.animation.clips:
            time_idx = self._accessor_index()
            self._create_bufferview(byte_length=clip.frames * 4, target=None)
            self._create_accessor(clip.frames, "SCALAR", ComponentType.FLOAT)

            sampler_idx = 0
            samplers = []
            channels = []

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

            self.ctx["GLTF"]["animations"].append(dict(name=clip.name, samplers=samplers, channels=channels))

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
            self._add_bindmatrix()

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
            # XYZ Position
            self.write(mesh.positions.tobytes())

            # UV Texture
            if self.data.flags[Flag.UV]:
                self.write(mesh.textures.tobytes())

            # XYZ Normals
            if self.data.flags[Flag.NORMALS]:
                self.write(mesh.normals.tobytes())

            # Bone Links
            if self._skeleton_presented:
                # Joint Indices
                self.write(mesh.links_ids.tobytes())

                # Joint Weights
                self.write(mesh.links_weights.tobytes())

            # ABC Polygons
            self.write(mesh.polygons.flatten().tobytes())

    def _add_bindmatrix(self):
        # Skeleton bones bind matrix
        bind_matrix = self.data.scene.skeleton.inverse_bind_matrices(transpose=True).tobytes()
        self.write(bind_matrix)

    def _add_animation(self):
        for clip in self.data.scene.animation.clips:
            self.write(clip.times.tobytes())

            for bone in self.data.scene.skeleton.bones:
                bone_transforms = clip.transforms[:, bone.id, :]
                rotations, translations = np.split(bone_transforms, [4], axis=1)

                self.write(translations.tobytes())
                self.write(rotations.tobytes())
