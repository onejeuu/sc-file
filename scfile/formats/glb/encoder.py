import json
import struct
from copy import deepcopy
from typing import Optional

from scfile.consts import FileSignature
from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F
from scfile.formats.mcsa.flags import Flag
from scfile.geometry.skeleton import euler_to_quat

from . import base
from .enums import BufferTarget, ComponentType


VERSION = 2


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

        gltf = json.dumps(self.ctx["GLTF"])

        self.write(struct.pack("<I", len(gltf)))
        self.write(b"JSON")
        self.write(gltf.encode())

    def create_gltf(self):
        self.ctx["GLTF"] = deepcopy(base.GLTF)
        self.ctx["BUFFER_VIEW_OFFSET"] = 0

        # Create scene
        scene = deepcopy(base.SCENE)
        self.ctx["GLTF"]["scenes"].append(scene)

        # Create nodes
        self.create_nodes()
        self.count_nodes()

        # Write length in buffers
        self.ctx["GLTF"]["buffers"].append(deepcopy(base.BUFFER))
        self.ctx["GLTF"]["buffers"][0]["byteLength"] = self.ctx["BUFFER_VIEW_OFFSET"]

    def create_nodes(self):
        self.create_meshes()

        if self.skeleton_presented:
            self.create_bones()

    def count_nodes(self):
        nodes = list(range(len(self.data.meshes)))

        if self.skeleton_presented:
            nodes += self.ctx["ROOT_BONE_INDEXES"]

        self.ctx["GLTF"]["scenes"][0]["nodes"] = nodes

    def create_meshes(self):
        def accessor_index() -> int:
            return len(self.ctx["GLTF"]["accessors"])

        for index, mesh in enumerate(self.data.meshes):
            primitive = deepcopy(base.PRIMITIVE)

            # XYZ Position
            primitive["attributes"]["POSITION"] = accessor_index()
            self.create_bufferview(byte_length=mesh.count.vertices * 3 * 4)
            self.create_accessor(mesh.count.vertices, "VEC3")

            # UV Texture
            if self.data.flags[Flag.TEXTURE]:
                primitive["attributes"]["TEXCOORD_0"] = accessor_index()
                self.create_bufferview(byte_length=mesh.count.vertices * 2 * 4)
                self.create_accessor(mesh.count.vertices, "VEC2")

            # XYZ Normals
            if self.data.flags[Flag.NORMALS]:
                primitive["attributes"]["NORMAL"] = accessor_index()
                self.create_bufferview(byte_length=mesh.count.vertices * 3 * 4)
                self.create_accessor(mesh.count.vertices, "VEC3")

            # Bone Links
            if self.skeleton_presented:
                # Joint Indices
                primitive["attributes"]["JOINTS_0"] = accessor_index()
                self.create_bufferview(byte_length=mesh.count.vertices * 4 * 1)
                self.create_accessor(mesh.count.vertices, "VEC4", ComponentType.UBYTE)

                # Joint Weights
                primitive["attributes"]["WEIGHTS_0"] = accessor_index()
                self.create_bufferview(byte_length=mesh.count.vertices * 4 * 4)
                self.create_accessor(mesh.count.vertices, "VEC4", ComponentType.FLOAT)

                # Bind Matrix
                bones_count = len(self.data.skeleton.bones)
                joint_offset = len(self.data.meshes)

                joints = list(range(bones_count))
                joints = [joint_offset + j for j in joints]

                self.ctx["GLTF"]["skins"] = [dict(name="Armature", inverseBindMatrices=accessor_index(), joints=joints)]
                self.create_bufferview(byte_length=bones_count * 16 * 4, target=None)
                self.create_accessor(bones_count, "MAT4", ComponentType.FLOAT)

            # ABC Polygons
            primitive["indices"] = accessor_index()
            self.create_bufferview(byte_length=mesh.count.polygons * 4 * 3, target=BufferTarget.ELEMENT_ARRAY_BUFFER)
            self.create_accessor(mesh.count.polygons * 3, "SCALAR", ComponentType.UINT32)

            # Create nodes
            primitive["material"] = index

            node = {"name": mesh.name, "mesh": index}

            if self.skeleton_presented:
                node["skin"] = 0

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)
            self.ctx["GLTF"]["meshes"].append({"name": mesh.name, "primitives": [primitive]})
            self.ctx["GLTF"]["materials"].append({"name": mesh.material})

    def create_bones(self):
        self.ctx["ROOT_BONE_INDEXES"] = []

        node_index_offset = len(self.data.meshes)

        for index, bone in enumerate(self.data.skeleton.bones, start=node_index_offset):
            node = {
                "name": bone.name,
                "rotation": euler_to_quat(bone.rotation),
                "translation": list(bone.position),
            }

            if bone.is_root:
                self.ctx["ROOT_BONE_INDEXES"].append(index)

            if bone.children:
                node["children"] = [node_index_offset + child.id for child in bone.children]

            # Add to GLTF
            self.ctx["GLTF"]["nodes"].append(node)

    def create_bufferview(self, byte_length: int, target: Optional[BufferTarget] = BufferTarget.ARRAY_BUFFER):
        view = {
            "buffer": 0,
            "byteLength": byte_length,
            "byteOffset": self.ctx["BUFFER_VIEW_OFFSET"],
        }

        if target:
            view["target"] = target

        self.ctx["GLTF"]["bufferViews"].append(view)
        self.ctx["BUFFER_VIEW_OFFSET"] += byte_length

    def create_accessor(self, count: int, accessor_type: str, component_type: ComponentType = ComponentType.FLOAT):
        buffer_view_idx = len(self.ctx["GLTF"]["bufferViews"]) - 1
        accessor = {
            "bufferView": buffer_view_idx,
            "count": count,
            "componentType": component_type,
            "type": accessor_type,
        }

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
            self.write(struct.pack(f"{mesh.count.vertices * 3}{F.F32}", *mesh.get_positions()))

            # UV Texture
            if self.data.flags[Flag.TEXTURE]:
                self.write(struct.pack(f"{mesh.count.vertices * 2}{F.F32}", *mesh.get_textures()))

            # XYZ Normals
            if self.data.flags[Flag.NORMALS]:
                self.write(struct.pack(f"{mesh.count.vertices * 3}{F.F32}", *mesh.get_normals()))

            # Bone Links
            if self.skeleton_presented:
                # Joint Indices
                self.write(struct.pack(f"{mesh.count.vertices * 4}{F.U8}", *mesh.get_bone_ids(max_links=4)))

                # Joint Weights
                self.write(struct.pack(f"{mesh.count.vertices * 4}{F.F32}", *mesh.get_bone_weights(max_links=4)))

                # Bind Matrix
                data = self.data.skeleton.inverse_bind_matrices(transpose=True)
                array = struct.pack(f"{len(self.data.skeleton.bones) * 16}{F.F32}", *data.flatten().tolist())
                self.write(array)

            # ABC Polygons
            self.write(struct.pack(f"{mesh.count.polygons * 3}{F.U32}", *mesh.get_polygons()))
