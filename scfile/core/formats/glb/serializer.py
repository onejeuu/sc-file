import json
import struct
from copy import deepcopy
from enum import IntEnum
from typing import Any, Callable, Optional

from scfile.consts import FileSignature
from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.utils.model.data import Polygon, Texture, Vector
from scfile.utils.model.vertex import Vertex


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
        self.buffer.write(struct.pack("<I", 0))  # total size

    def update_total_size(self):
        self.buffer.seek(8)
        self.buffer.write(struct.pack("<I", len(self.buffer.getvalue())))

    # that too bad
    def create_vertex_array(self, vertices: list[Vertex], attribute: Callable[[Vertex], Vector | Texture], count: int):
        fmt = ByteOrder.LITTLE + F.F32 * len(vertices) * count
        return struct.pack(fmt, *[value for vertex in vertices for value in attribute(vertex)])

    def create_polygon_array(self, polygons: list[Polygon]):
        fmt = ByteOrder.LITTLE + F.U32 * len(polygons) * 3  # not sure
        return struct.pack(fmt, *[value for polygon in polygons for value in polygon])

    def add_binary_chunk(self):
        # Size of BIN chunk placeholder
        chunk_start = self.buffer.tell()
        self.buffer.write(struct.pack("<I", 0))
        self.buffer.write(b"BIN\0")

        start = self.buffer.tell()

        for mesh in self.model.meshes:
            array = self.create_vertex_array(mesh.vertices, lambda v: v.position, count=3)
            self.buffer.write(array)

            if self.flags[Flag.TEXTURE]:
                array = self.create_vertex_array(mesh.vertices, lambda v: v.texture, count=2)
                self.buffer.write(array)

            if self.flags[Flag.NORMALS]:
                array = self.create_vertex_array(mesh.vertices, lambda v: v.normals, count=3)
                self.buffer.write(array)

            array = self.create_polygon_array(mesh.polygons)
            self.buffer.write(array)

        end = self.buffer.tell()
        size = end - start

        # Write size of BIN chunk
        self.buffer.seek(chunk_start)
        self.buffer.write(struct.pack("<I", size))

    def add_json_chunk(self):
        self.create_gltf()

        gltf = json.dumps(self.gltf).encode()

        self.buffer.write(struct.pack("<I", len(gltf)))
        self.buffer.write(b"JSON")
        self.buffer.write(gltf)

    # ! impossible to read
    def create_gltf(self):
        self.gltf = deepcopy(DEFAULT_GLTF)

        # why offset flipping back and forth like a whore
        offset = 0

        for mesh_idx, mesh in enumerate(self.model.meshes):
            primitive = {
                "attributes": {},
                "mode": 4,  # TRIANGLES # ! MAGIC VALUE
            }

            position_accessor_idx, _, offset = self.create_attribute(
                mesh.vertices, lambda v: list(v.position), "VEC3", 3, offset
            )
            primitive["attributes"]["POSITION"] = position_accessor_idx

            if self.flags[Flag.TEXTURE]:
                texcoord_accessor_idx, _, offset = self.create_attribute(
                    mesh.vertices, lambda v: list(v.texture), "VEC2", 2, offset
                )
                primitive["attributes"]["TEXCOORD_0"] = texcoord_accessor_idx

            if self.flags[Flag.NORMALS]:
                normal_accessor_idx, _, offset = self.create_attribute(
                    mesh.vertices, lambda v: list(v.normals), "VEC3", 3, offset
                )
                primitive["attributes"]["NORMAL"] = normal_accessor_idx

            if self.flags[Flag.SKELETON]:
                pass

            indices_accessor_idx, offset = self.create_indices(mesh.polygons, offset)
            primitive["indices"] = indices_accessor_idx

            self.gltf["meshes"].append({"name": mesh.name, "primitives": [primitive]})
            self.gltf["nodes"].append({"mesh": mesh_idx, "name": mesh.name})
            self.gltf["scenes"][0]["nodes"].append(mesh_idx)

        self.gltf["buffers"][0]["byteLength"] = offset

    def create_accessor(
        self,
        buffer_view_index: int,
        component_type: ComponentType,
        accessor_type: str,
        count: int,
        min_values: Optional[list[float]] = None,
        max_values: Optional[list[float]] = None,
    ) -> dict:
        accessor = {
            "bufferView": buffer_view_index,
            "componentType": component_type,
            "count": count,
            "type": accessor_type,
        }

        if min_values is not None:
            accessor["min"] = min_values
        if max_values is not None:
            accessor["max"] = max_values

        return accessor

    # ! its awful
    def create_attribute(
        self,
        vertices: list[Any],
        attribute_data_func,
        accessor_type: str,
        component_count: int,
        offset: int,
    ) -> tuple[int, int, int]:
        data = [attribute_data_func(v) for v in vertices]
        byte_length = len(data) * component_count * 4  # ! MAGIC VALUE

        buffer_view_idx = len(self.gltf["bufferViews"])
        accessor_idx = len(self.gltf["accessors"])

        self.gltf["bufferViews"].append(
            {"buffer": 0, "byteOffset": offset, "byteLength": byte_length, "target": BufferTarget.ARRAY_BUFFER}
        )

        min_values = [min(p[i] for p in data) for i in range(component_count)]
        max_values = [max(p[i] for p in data) for i in range(component_count)]

        self.gltf["accessors"].append(
            self.create_accessor(buffer_view_idx, ComponentType.FLOAT, accessor_type, len(data), min_values, max_values)
        )

        return accessor_idx, buffer_view_idx, offset + byte_length

    def create_indices(self, polygons: list[Polygon], offset: int) -> tuple[int, int]:
        indices = [i for polygon in polygons for i in polygon]
        byte_length = len(indices) * 4  # uint32 # ! MAGIC VALUE

        buffer_view_idx = len(self.gltf["bufferViews"])
        accessor_idx = len(self.gltf["accessors"])

        self.gltf["bufferViews"].append(
            {"buffer": 0, "byteOffset": offset, "byteLength": byte_length, "target": BufferTarget.ELEMENT_ARRAY_BUFFER}
        )

        # not always uint32 dumbass
        self.gltf["accessors"].append(
            self.create_accessor(buffer_view_idx, ComponentType.UINT32, "SCALAR", len(indices))
        )

        return accessor_idx, offset + byte_length
