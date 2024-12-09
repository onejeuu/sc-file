import json
import struct
from copy import deepcopy
from enum import IntEnum
from typing import Any, Callable, Optional, TypeAlias, TypedDict

from scfile.consts import FileSignature
from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.utils.model.data import Polygon, Texture, Vector
from scfile.utils.model.vertex import Vertex


VertexAttribute: TypeAlias = Callable[[Vertex], Vector | Texture]


VERSION = 2

DEFAULT_GLTF = {
    "asset": {"version": "2.0", "generator": "onejeuu@scfile"},
    "scene": 0,
    "scenes": [{"nodes": []}],
    "nodes": [],
    "meshes": [],
    "accessors": [],
    "bufferViews": [],
    "buffers": [{"byteLength": 0}],
}


class ComponentType(IntEnum):
    FLOAT = 5126
    UINT16 = 5123
    UINT32 = 5125


class BufferTarget(IntEnum):
    ARRAY_BUFFER = 34962
    ELEMENT_ARRAY_BUFFER = 34963


class PrimitiveMode(IntEnum):
    TRIANGLES = 4


class Accessor(TypedDict):
    bufferView: int
    componentType: ComponentType
    type: str
    count: int
    min: Optional[list[float]]
    max: Optional[list[float]]


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

    def create_vertex_array(self, vertices: list[Vertex], attribute: VertexAttribute, count: int):
        fmt = ByteOrder.LITTLE + F.F32 * len(vertices) * count
        return struct.pack(fmt, *[value for vertex in vertices for value in attribute(vertex)])

    def create_polygon_array(self, polygons: list[Polygon]):
        fmt = ByteOrder.LITTLE + F.U32 * len(polygons) * 3
        return struct.pack(fmt, *[value for polygon in polygons for value in polygon])

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

            # ABC Polygons
            array = self.create_polygon_array(mesh.polygons)
            self.buffer.write(array)

        # Write size of BIN chunk
        end = self.buffer.tell()
        size = end - start

        self.buffer.seek(chunk_start)
        self.buffer.write(struct.pack("<I", size))

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

        for mesh_idx, mesh in enumerate(self.model.meshes):
            primitive = {
                "attributes": {},
                "mode": PrimitiveMode.TRIANGLES,
            }

            # XYZ Position
            primitive["attributes"]["POSITION"] = len(self.gltf["accessors"])
            self.create_attribute(mesh.vertices, lambda v: v.position, "VEC3", 3)

            # UV Texture
            if self.flags[Flag.TEXTURE]:
                primitive["attributes"]["TEXCOORD_0"] = len(self.gltf["accessors"])
                self.create_attribute(mesh.vertices, lambda v: v.texture, "VEC2", 2)

            # XYZ Normals
            if self.flags[Flag.NORMALS]:
                primitive["attributes"]["NORMAL"] = len(self.gltf["accessors"])
                self.create_attribute(mesh.vertices, lambda v: v.normals, "VEC3", 3)

            # TODO
            if self.flags[Flag.SKELETON]:
                pass

            # ABC Polygons
            primitive["indices"] = len(self.gltf["accessors"])
            self.create_indices(mesh.polygons)

            # Meshes and nodes
            self.gltf["meshes"].append({"name": mesh.name, "primitives": [primitive]})
            self.gltf["nodes"].append({"mesh": mesh_idx, "name": mesh.name})
            self.gltf["scenes"][0]["nodes"].append(mesh_idx)

        self.gltf["buffers"][0]["byteLength"] = self.attribute_offset

    def create_attribute(self, vertices: list[Any], attribute: VertexAttribute, accessor_type: str, count: int):
        # Prepare vertex data
        data = [list(attribute(v)) for v in vertices]

        # Add buffer view
        byte_length = len(data) * count * 4  # uint32
        buffer_view_idx = len(self.gltf["bufferViews"])

        self.gltf["bufferViews"].append(
            {
                "buffer": 0,
                "byteOffset": self.attribute_offset,
                "byteLength": byte_length,
                "target": BufferTarget.ARRAY_BUFFER,
            }
        )

        # Move offset
        self.attribute_offset += byte_length

        # Attribute boundaries
        min_values = list(map(min, zip(*data)))
        max_values = list(map(max, zip(*data)))

        # Add accessor
        self.gltf["accessors"].append(
            Accessor(
                bufferView=buffer_view_idx,
                componentType=ComponentType.FLOAT,
                type=accessor_type,
                count=len(data),
                min=min_values,
                max=max_values,
            )
        )

    def create_indices(self, polygons: list[Polygon]):
        # Prepare polygon data
        indices = [i for polygon in polygons for i in polygon]

        # Add buffer view
        byte_length = len(indices) * 4  # uint32
        buffer_view_idx = len(self.gltf["bufferViews"])

        self.gltf["bufferViews"].append(
            {
                "buffer": 0,
                "byteOffset": self.attribute_offset,
                "byteLength": byte_length,
                "target": BufferTarget.ELEMENT_ARRAY_BUFFER,
            }
        )

        # Add accessor
        self.gltf["accessors"].append(
            Accessor(
                bufferView=buffer_view_idx,
                componentType=ComponentType.UINT32,
                type="SCALAR",
                count=len(indices),
                min=None,
                max=None,
            )
        )
