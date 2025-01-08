import json
import struct
from copy import deepcopy
from enum import IntEnum
from itertools import chain, islice, repeat
from typing import Callable, Sized, TypeAlias

import numpy as np

from scfile.consts import CLI, FileSignature
from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.utils.model.data import Polygon, Texture, Vector
from scfile.utils.model.skeleton import create_transform_matrix
from scfile.utils.model.vertex import Vertex


VertexAttribute: TypeAlias = Callable[[Vertex], Vector | Texture | list[int] | list[float]]


VERSION = 2

DEFAULT_GLTF = {
    "asset": {"version": "2.0", "generator": f"onejeuu@scfile v{CLI.VERSION}"},
    "scene": 0,
    "scenes": [],
    "nodes": [],
    "meshes": [],
    "skins": [],
    "accessors": [],
    "bufferViews": [],
    "buffers": [],
}

DEFAULT_SCENE = {"name": "Scene", "nodes": []}
DEFAULT_BUFFER = {"byteLength": 0}


class ComponentType(IntEnum):
    UBYTE = 5121
    FLOAT = 5126
    UINT16 = 5123
    UINT32 = 5125


class BufferTarget(IntEnum):
    ARRAY_BUFFER = 34962
    ELEMENT_ARRAY_BUFFER = 34963


class PrimitiveMode(IntEnum):
    TRIANGLES = 4


class GlbSerializer(FileSerializer[ModelData]):
    @property
    def model(self):
        return self.data.model

    @property
    def flags(self):
        return self.data.flags

    def serialize(self):
        self.add_header()
        self.add_json_chunk()
        self.add_binary_chunk()
        self.update_total_size()

    def add_header(self):
        self.buffer.write(FileSignature.GLTF)
        self.buffer.write(struct.pack("<I", VERSION))
        self.buffer.write(struct.pack("<I", 0))  # Total size placeholder

    def update_total_size(self):
        self.buffer.seek(8)
        self.buffer.write(struct.pack("<I", len(self.buffer.getvalue())))

    def create_vertex_array(self, vertices: list[Vertex], attribute: VertexAttribute, count: int, data_type: F = F.F32):
        fmt = ByteOrder.LITTLE + (data_type * len(vertices) * count)
        return struct.pack(fmt, *[value for vertex in vertices for value in attribute(vertex)])

    def create_polygon_array(self, polygons: list[Polygon]):
        fmt = ByteOrder.LITTLE + (F.U32 * len(polygons) * 3)
        return struct.pack(fmt, *[value for polygon in polygons for value in polygon])

    def add_json_chunk(self):
        self.create_gltf()

        gltf = json.dumps(self.gltf).encode()

        self.buffer.write(struct.pack("<I", len(gltf)))
        self.buffer.write(b"JSON")
        self.buffer.write(gltf)

    def add_bones(self):
        from scipy.spatial.transform import Rotation as R

        # Root bones indexes
        self.roots_idx: list[int] = []

        if self.flags[Flag.SKELETON]:
            for bone in self.model.skeleton.bones:
                if bone.is_root:
                    self.roots_idx.append(self.node_offset)

                self.node_offset += 1

                rotation = R.from_euler("xyz", list(bone.rotation), degrees=True)
                node = {
                    "name": bone.name,
                    "rotation": rotation.as_quat().tolist(),
                    "translation": list(bone.position),
                }

                if bone.children:
                    node["children"] = [child.id for child in bone.children]

                # Add to GLTF
                self.gltf["nodes"].append(node)

    def add_meshes(self):
        # Mesh indexes
        self.mesh_idx: list[int] = []

        for index, mesh in enumerate(self.model.meshes):
            self.mesh_idx.append(self.node_offset)
            self.node_offset += 1

            primitive = {
                "attributes": {},
                "mode": PrimitiveMode.TRIANGLES,
            }

            # XYZ Position
            primitive["attributes"]["POSITION"] = len(self.gltf["accessors"])
            self.create_attribute([v.position for v in mesh.vertices], "VEC3", bytes_per_item=3 * 4, boundaries=True)

            # UV Texture
            if self.flags[Flag.TEXTURE]:
                primitive["attributes"]["TEXCOORD_0"] = len(self.gltf["accessors"])
                self.create_attribute([v.texture for v in mesh.vertices], "VEC2", bytes_per_item=2 * 4, boundaries=True)

            # XYZ Normals
            if self.flags[Flag.NORMALS]:
                primitive["attributes"]["NORMAL"] = len(self.gltf["accessors"])
                self.create_attribute([v.normals for v in mesh.vertices], "VEC3", bytes_per_item=3 * 4, boundaries=True)

            # Bone Links
            if self.flags[Flag.SKELETON]:
                # Joint Indices
                primitive["attributes"]["JOINTS_0"] = len(self.gltf["accessors"])
                self.create_attribute(
                    [v.bone_ids for v in mesh.vertices],
                    "VEC4",
                    component_type=ComponentType.UBYTE,
                    bytes_per_item=4,
                )

                # Joint Weights
                primitive["attributes"]["WEIGHTS_0"] = len(self.gltf["accessors"])
                self.create_attribute(
                    [v.bone_weights for v in mesh.vertices],
                    "VEC4",
                    component_type=ComponentType.FLOAT,
                    bytes_per_item=4 * 4,
                )

                # Bind Matrix
                self.add_skin()
                self.create_attribute(
                    self.model.skeleton.bones,
                    "MAT4",
                    component_type=ComponentType.FLOAT,
                    bytes_per_item=4 * 4 * 4,
                )

            # ABC Polygons
            primitive["indices"] = len(self.gltf["accessors"])
            self.create_attribute(
                [i for p in mesh.polygons for i in p],
                "SCALAR",
                component_type=ComponentType.UINT32,
                target=BufferTarget.ELEMENT_ARRAY_BUFFER,
                bytes_per_item=4,
            )

            # Create nodes
            meshnode = {"name": mesh.name, "primitives": [primitive]}

            node = {"name": mesh.name, "mesh": index}
            if self.flags[Flag.SKELETON]:
                node["skin"] = 0

            # Add to GLTF
            self.gltf["nodes"].append(node)
            self.gltf["meshes"].append(meshnode)

    def add_skin(self):
        self.gltf["skins"] = [
            {
                "name": "Armature",
                "inverseBindMatrices": len(self.gltf["accessors"]),
                "joints": list(range(len(self.model.skeleton.bones))),
            }
        ]

    def add_armature(self):
        if self.flags[Flag.SKELETON]:
            node = {"name": "Armature", "children": [*self.roots_idx, *self.mesh_idx]}
            self.gltf["nodes"].append(node)

    def create_gltf(self):
        # Copy template
        self.gltf = deepcopy(DEFAULT_GLTF)

        # Add attributes to gltf json
        self.attribute_offset = 0
        self.node_offset = 0

        # Create scene node
        self.gltf["scenes"].append(deepcopy(DEFAULT_SCENE))

        # Add nodes
        self.add_bones()
        self.add_meshes()
        self.add_armature()

        # Write nodes count
        self.gltf["scenes"][0]["nodes"] = [self.node_offset]

        # Write length in buffers
        self.gltf["buffers"].append(deepcopy(DEFAULT_BUFFER))
        self.gltf["buffers"][0]["byteLength"] = self.attribute_offset

    def create_attribute(
        self,
        data: Sized,
        accessor_type: str,
        component_type: ComponentType = ComponentType.FLOAT,
        target: BufferTarget = BufferTarget.ARRAY_BUFFER,
        bytes_per_item: int = 4,
        boundaries: bool = False,
    ):
        # Add buffer view
        count = len(data)
        byte_length = count * bytes_per_item
        buffer_view_idx = len(self.gltf["bufferViews"])

        self.gltf["bufferViews"].append(
            {
                "buffer": 0,
                "byteLength": byte_length,
                "byteOffset": self.attribute_offset,
                "target": target,
            }
        )

        # Move offset
        self.attribute_offset += byte_length

        # Create accessor
        accessor = {
            "bufferView": buffer_view_idx,
            "componentType": component_type,
            "count": count,
            "type": accessor_type,
        }

        # Attribute boundaries
        if boundaries:
            accessor["min"] = list(map(min, zip(*data)))
            accessor["max"] = list(map(max, zip(*data)))

        # Add accessor
        self.gltf["accessors"].append(accessor)

    def add_binary_chunk(self):
        # Size of BIN chunk placeholder
        chunk_start = self.buffer.tell()
        self.buffer.write(struct.pack("<I", 0))
        self.buffer.write(b"BIN\0")

        # Mesh data arrays
        start = self.buffer.tell()

        for mesh in self.model.meshes:
            # XYZ Position
            array = self.create_vertex_array(mesh.vertices, lambda v: v.position, count=3)
            self.buffer.write(array)

            # UV Texture
            if self.flags[Flag.TEXTURE]:
                array = self.create_vertex_array(mesh.vertices, lambda v: v.texture, count=2)
                self.buffer.write(array)

            # XYZ Normals
            if self.flags[Flag.NORMALS]:
                array = self.create_vertex_array(mesh.vertices, lambda v: v.normals, count=3)
                self.buffer.write(array)

            # Bone Links
            if self.flags[Flag.SKELETON]:
                # Joint Indices
                array = self.create_vertex_array(
                    mesh.vertices,
                    lambda v: list(islice(chain(v.bone_ids, repeat(0)), 4)),
                    count=4,
                    data_type=F.U8,
                )
                self.buffer.write(array)

                # Joint Weights
                array = self.create_vertex_array(
                    mesh.vertices,
                    lambda v: list(islice(chain(v.bone_weights, repeat(0.0)), 4)),
                    count=4,
                    data_type=F.F32,
                )
                self.buffer.write(array)

                # Bind Matrix
                fmt = ByteOrder.LITTLE + (F.F32 * len(self.model.skeleton.bones) * 16)
                data = np.array(self.model.skeleton.calculate_inverse_bind_matrices())
                array = struct.pack(fmt, *data.flatten().tolist())
                self.buffer.write(array)

            # ABC Polygons
            array = self.create_polygon_array(mesh.polygons)
            self.buffer.write(array)

        # Write size of BIN chunk
        end = self.buffer.tell()
        size = end - start

        self.buffer.seek(chunk_start)
        self.buffer.write(struct.pack("<I", size))
