import json
import struct
from copy import deepcopy
from enum import IntEnum
from itertools import chain, islice, repeat
from typing import Callable, Sized, TypeAlias

from scfile.consts import CLI, FileSignature, McsaModel
from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.utils.model.data import Polygon, Texture, Vector
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

    def create_gltf(self):
        # Copy template
        self.gltf = deepcopy(DEFAULT_GLTF)

        # Add attributes to gltf json
        self.attribute_offset = 0
        self.node_offset = 0

        # Create scene nodes
        self.gltf["scenes"].append(deepcopy(DEFAULT_SCENE))

        # Add skeleton
        if self.flags[Flag.SKELETON]:
            from scipy.spatial.transform import Rotation as R

            for index, bone in enumerate(self.model.skeleton.bones):
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
                self.node_offset += 1

                # Add root bones to node indexes
                if bone.parent_id == McsaModel.ROOT_BONE_ID:
                    self.gltf["scenes"][0]["nodes"].append(index)

            # Create skin
            self.gltf["skins"] = [
                {
                    "name": "Armature",
                    "joints": list(range(len(self.model.skeleton.bones))),
                    # "skeleton": len(self.gltf["scenes"][0]["nodes"]),  # TODO: handle no meshes case
                }
            ]

        # Add meshes
        for index, mesh in enumerate(self.model.meshes):
            primitive = {
                "attributes": {},
                "mode": PrimitiveMode.TRIANGLES,
            }

            # XYZ Position
            primitive["attributes"]["POSITION"] = len(self.gltf["accessors"])
            self.create_attribute([v.position for v in mesh.vertices], "VEC3", bytes_per_item=3 * 4)

            # UV Texture
            if self.flags[Flag.TEXTURE]:
                primitive["attributes"]["TEXCOORD_0"] = len(self.gltf["accessors"])
                self.create_attribute([v.texture for v in mesh.vertices], "VEC2", bytes_per_item=2 * 4)

            # XYZ Normals
            if self.flags[Flag.NORMALS]:
                primitive["attributes"]["NORMAL"] = len(self.gltf["accessors"])
                self.create_attribute([v.normals for v in mesh.vertices], "VEC3", bytes_per_item=3 * 4)

            # TODO
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

            # ABC Polygons
            primitive["indices"] = len(self.gltf["accessors"])
            self.create_attribute(
                [i for p in mesh.polygons for i in p],
                "SCALAR",
                component_type=ComponentType.UINT32,
                target=BufferTarget.ELEMENT_ARRAY_BUFFER,
                bytes_per_item=4,
            )

            # Add mesh to scene
            node = {"mesh": index, "name": mesh.name}
            if self.flags[Flag.SKELETON]:
                node["skin"] = 0

            mesh = {"name": mesh.name, "primitives": [primitive]}

            # Add to GLTF
            self.gltf["nodes"].append(node)
            self.gltf["meshes"].append(mesh)
            self.gltf["scenes"][0]["nodes"].append(index + self.node_offset)

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

        # Add accessor
        if "VEC" not in accessor_type:
            self.gltf["accessors"].append(
                {
                    "bufferView": buffer_view_idx,
                    "componentType": component_type,
                    "count": count,
                    "type": accessor_type,
                }
            )

        else:
            # Attribute boundaries
            min_values = list(map(min, zip(*data)))
            max_values = list(map(max, zip(*data)))

            self.gltf["accessors"].append(
                {
                    "bufferView": buffer_view_idx,
                    "componentType": component_type,
                    "count": count,
                    "type": accessor_type,
                    "min": min_values,
                    "max": max_values,
                }
            )

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

            # TODO
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

            # ABC Polygons
            array = self.create_polygon_array(mesh.polygons)
            self.buffer.write(array)

        # Write size of BIN chunk
        end = self.buffer.tell()
        size = end - start

        self.buffer.seek(chunk_start)
        self.buffer.write(struct.pack("<I", size))
