import json
import struct
from copy import deepcopy
from itertools import chain, islice, repeat
from typing import NamedTuple, Optional, Self, Sized

import numpy as np

from scfile.consts import FileSignature
from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F
from scfile.formats.mcsa.flags import Flag

from .consts import BASE_BUFFER, BASE_GLTF, BASE_PRIMITIVE, BASE_SCENE, VERSION
from .enums import BufferTarget, ComponentType


class Bounds(NamedTuple):
    min_values: list[float]
    max_values: list[float]

    @classmethod
    def calculate(cls, data: Sized) -> Self:
        return cls(
            min_values=list(map(min, zip(*data))),
            max_values=list(map(max, zip(*data))),
        )


class GlbEncoder(FileEncoder[ModelContent, ModelOptions]):
    format = FileFormat.GLB
    signature = FileSignature.GLTF

    _options = ModelOptions

    @property
    def skeleton_presented(self) -> bool:
        return self.data.flags[Flag.SKELETON] and self.options.parse_skeleton

    def prepare(self):
        self.data.scene.ensure_unique_names()
        self.data.scene.skeleton.convert_to_local()
        self.data.scene.skeleton.build_hierarchy()

    def serialize(self):
        self.add_header()
        self.add_json_chunk()
        self.add_binary_chunk()
        self.update_total_size()

    def add_header(self):
        self.write(struct.pack("<I", VERSION))

        # Total Size Placeholder
        self.ctx["TOTAL_SIZE_POS"] = self.tell()
        self.write(struct.pack("<I", 0))

    def update_total_size(self):
        self.seek(self.ctx["TOTAL_SIZE_POS"])
        self.write(struct.pack("<I", len(self.getvalue())))

    def add_json_chunk(self):
        self.create_gltf()

        gltf = json.dumps(self.ctx["GLTF"], indent=2)

        self.write(struct.pack("<I", len(gltf)))
        self.write(b"JSON")
        self.write(gltf.encode())

    def create_gltf(self):
        self.ctx["GLTF"] = deepcopy(BASE_GLTF)
        self.ctx["BUFFER_VIEW_OFFSET"] = 0

        # Create scene
        scene = deepcopy(BASE_SCENE)
        self.ctx["GLTF"]["scenes"].append(scene)

        self.create_nodes()
        self.count_nodes()

        # Write length in buffers
        self.ctx["GLTF"]["buffers"].append(deepcopy(BASE_BUFFER))
        self.ctx["GLTF"]["buffers"][0]["byteLength"] = self.ctx["BUFFER_VIEW_OFFSET"]

    def create_nodes(self):
        self.create_meshes()

        if self.skeleton_presented:
            self.create_bones()
            # self.create_armature()

    def count_nodes(self):
        nodes = list(range(len(self.data.meshes)))

        if self.skeleton_presented:
            nodes += self.ctx["ROOT_BONE_INDEXES"]

        self.ctx["GLTF"]["scenes"][0]["nodes"] = nodes

    def create_meshes(self):
        def accessor_index() -> int:
            return len(self.ctx["GLTF"]["accessors"])

        for index, mesh in enumerate(self.data.meshes):
            primitive = deepcopy(BASE_PRIMITIVE)

            # XYZ Position
            primitive["attributes"]["POSITION"] = accessor_index()
            bounds = Bounds.calculate([v.position for v in mesh.vertices])
            self.create_bufferview(byte_length=mesh.count.vertices * 3 * 4)
            self.create_accessor(mesh.count.vertices, "VEC3", bounds=bounds)

            # UV Texture
            if self.data.flags[Flag.TEXTURE]:
                primitive["attributes"]["TEXCOORD_0"] = accessor_index()
                bounds = Bounds.calculate([v.texture for v in mesh.vertices])
                self.create_bufferview(byte_length=mesh.count.vertices * 2 * 4)
                self.create_accessor(mesh.count.vertices, "VEC2", bounds=bounds)

            # XYZ Normals
            if self.data.flags[Flag.NORMALS]:
                primitive["attributes"]["NORMAL"] = accessor_index()
                bounds = Bounds.calculate([v.normals for v in mesh.vertices])
                self.create_bufferview(byte_length=mesh.count.vertices * 3 * 4)
                self.create_accessor(mesh.count.vertices, "VEC3", bounds=bounds)

            # Bone Links
            if self.skeleton_presented:
                # Joint Indices
                primitive["attributes"]["JOINTS_0"] = accessor_index()
                bounds = Bounds.calculate([v.bone_ids for v in mesh.vertices])
                self.create_bufferview(byte_length=mesh.count.vertices * 4)
                self.create_accessor(mesh.count.vertices, "VEC4", ComponentType.UBYTE, bounds=bounds)

                # Joint Weights
                primitive["attributes"]["WEIGHTS_0"] = accessor_index()
                bounds = Bounds.calculate([v.bone_weights for v in mesh.vertices])
                self.create_bufferview(byte_length=mesh.count.vertices * 4 * 4)
                self.create_accessor(mesh.count.vertices, "VEC4", ComponentType.FLOAT, bounds=bounds)

                # Bind Matrix
                joints = list(range(len(self.data.skeleton.bones)))
                joints = [len(self.data.meshes) + j for j in joints]
                self.ctx["GLTF"]["skins"] = [dict(name="Armature", inverseBindMatrices=accessor_index(), joints=joints)]
                self.create_bufferview(byte_length=len(self.data.skeleton.bones) * 16 * 4)
                self.create_accessor(len(self.data.skeleton.bones), "MAT4", ComponentType.FLOAT)

            # ABC Polygons
            primitive["indices"] = accessor_index()
            self.create_bufferview(byte_length=mesh.count.polygons * 4 * 3, target=BufferTarget.ELEMENT_ARRAY_BUFFER)
            self.create_accessor(mesh.count.polygons * 3, "SCALAR", ComponentType.UINT32)

            # Create nodes
            node = {"name": mesh.name, "mesh": index}
            mesh_node = {"name": mesh.name, "primitives": [primitive]}

            if self.skeleton_presented:
                node["skin"] = 0

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)
            self.ctx["GLTF"]["meshes"].append(mesh_node)

    def create_bones(self):
        from scipy.spatial.transform import Rotation as R

        self.ctx["ROOT_BONE_INDEXES"] = []

        node_index_offset = len(self.data.scene.meshes)

        for index, bone in enumerate(self.data.skeleton.bones, start=node_index_offset):
            rotation = R.from_euler("xyz", list(bone.rotation), degrees=True)
            node = {
                "name": bone.name,
                "rotation": rotation.as_quat().tolist(),
                "translation": list(bone.position),
            }

            if bone.is_root:
                self.ctx["ROOT_BONE_INDEXES"].append(index)

            if bone.children:
                node["children"] = [node_index_offset + child.id for child in bone.children]

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)

    def create_armature(self):
        # children = list(range(len(self.data.scene.meshes)))
        # children += self.ctx["ROOT_BONE_INDEXES"]

        children = self.ctx["ROOT_BONE_INDEXES"]

        node = {"name": "Armature", "children": children}
        self.ctx["GLTF"]["nodes"].append(node)

    def create_bufferview(
        self,
        byte_length: int,
        target: BufferTarget = BufferTarget.ARRAY_BUFFER,
    ):
        self.ctx["GLTF"]["bufferViews"].append(
            {
                "buffer": 0,
                "byteLength": byte_length,
                "byteOffset": self.ctx["BUFFER_VIEW_OFFSET"],
                "target": target,
            }
        )
        self.ctx["BUFFER_VIEW_OFFSET"] += byte_length

    def create_accessor(
        self,
        count: int,
        accessor_type: str,
        component_type: ComponentType = ComponentType.FLOAT,
        bounds: Optional[Bounds] = None,
    ):
        buffer_view_idx = len(self.ctx["GLTF"]["bufferViews"]) - 1
        accessor = {
            "bufferView": buffer_view_idx,
            "count": count,
            "componentType": component_type,
            "type": accessor_type,
        }

        if bounds:
            accessor["min"] = bounds.min_values
            accessor["max"] = bounds.max_values

        self.ctx["GLTF"]["accessors"].append(accessor)

    def add_binary_chunk(self):
        self.add_bin_size()
        self.ctx["BIN_START"] = self.tell()
        self.add_meshes()
        self.ctx["BIN_END"] = self.tell()
        self.update_bin_size()

    def add_bin_size(self):
        # BIN Size Placeholder
        self.ctx["BIN_SIZE_POS"] = self.tell()
        self.write(struct.pack("<I", 0))
        self.write(b"BIN\0")

    def update_bin_size(self):
        size = self.ctx["BIN_END"] - self.ctx["BIN_START"]
        self.seek(self.ctx["BIN_SIZE_POS"])
        self.write(struct.pack("<I", size))

    def add_meshes(self):
        for mesh in self.data.meshes:
            # XYZ Position
            self.write(
                struct.pack(f"{mesh.count.vertices * 3}{F.F32}", *[i for v in mesh.vertices for i in v.position])
            )

            # UV Texture
            if self.data.flags[Flag.TEXTURE]:
                self.write(
                    struct.pack(f"{mesh.count.vertices * 2}{F.F32}", *[i for v in mesh.vertices for i in v.texture])
                )

            # XYZ Normals
            if self.data.flags[Flag.NORMALS]:
                self.write(
                    struct.pack(f"{mesh.count.vertices * 3}{F.F32}", *[i for v in mesh.vertices for i in v.normals])
                )

            # Bone Links
            if self.skeleton_presented:
                # Joint Indices
                self.write(
                    struct.pack(
                        f"{mesh.count.vertices * 4}{F.U8}",
                        *[i for v in mesh.vertices for i in list(islice(chain(v.bone_ids, repeat(0)), 4))],
                    )
                )

                # Joint Weights
                self.write(
                    struct.pack(
                        f"{mesh.count.vertices * 4}{F.F32}",
                        *[i for v in mesh.vertices for i in list(islice(chain(v.bone_weights, repeat(0.0)), 4))],
                    )
                )

                # Bind Matrix
                data = np.array(self.data.skeleton.calculate_inverse_bind_matrices())
                # data = np.flip(data, axis=1)

                array = struct.pack(f"{len(self.data.skeleton.bones) * 16}{F.F32}", *data.flatten().tolist())
                self.write(array)

            # ABC Polygons
            self.write(struct.pack(f"{mesh.count.polygons * 3}{F.U32}", *[i for p in mesh.polygons for i in p]))
