import struct
from dataclasses import dataclass
from enum import StrEnum, auto

from scfile.consts import FileSignature
from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.utils.model.mesh import ModelMesh
from scfile.utils.model.vertex import Vertex


VERSION = 2.0

CHUNK_SIZE = 8
GLB_SIZE = 12
ALIGNMENT = 4


class ChunkType(StrEnum):
    JSON = "JSON"
    BIN = "BIN\0"


class ComponentType(StrEnum):
    FLOAT = "5126"
    UINT16 = "5123"


class BufferTarget(StrEnum):
    ARRAY_BUFFER = "34962"
    ELEMENT_ARRAY_BUFFER = "34963"


class AttributeType(StrEnum):
    SCALAR = auto()
    VEC2 = auto()
    VEC3 = auto()
    VEC4 = auto()


class DataSize:
    positions = 12  # 3 floats
    normals = 12  # 3 floats
    uv = 8  # 2 floats
    weights = 16  # 4 floats
    joints = 8  # 4 uint16

    vertex = positions + normals + uv + weights + joints

    def __iter__(self):
        return iter((self.positions, self.normals, self.uv, self.weights, self.joints))


@dataclass
class BufferViewInfo:
    offset: int
    length: int
    stride: int
    target: BufferTarget


@dataclass
class AccessorInfo:
    view_index: int
    count: int
    component_type: ComponentType
    attribute_type: AttributeType


class GlbSerializer(FileSerializer[ModelData]):
    @property
    def model(self):
        return self.data.model

    @property
    def flags(self):
        return self.data.flags

    def serialize(self):
        self.add_header()

        json_start = self.buffer.tell()
        self.buffer.write(b"\0" * CHUNK_SIZE)

        binary_start = self.buffer.tell()
        self.buffer.write(b"\0" * CHUNK_SIZE)

        buffer_views = []
        accessors = []

        for mesh in self.model.meshes:
            # Pack mesh data and get buffer views
            mesh_views = self.pack_mesh_data(mesh)
            view_start_idx = len(buffer_views)
            buffer_views.extend(mesh_views)

            # Create accessors
            mesh_accessors = self.create_mesh_accessors(mesh, view_start_idx)
            accessors.extend(mesh_accessors)

    def align_to_4bytes(self):
        padding = (ALIGNMENT - (self.buffer.tell() % ALIGNMENT)) % ALIGNMENT
        if padding:
            self.buffer.write(b"\0" * padding)

    def add_header(self):
        self.buffer.write(FileSignature.GLTF)
        self.buffer.write(struct.pack("<I", VERSION))
        self.buffer.write(struct.pack("<I", 0))  # total size

    def pack_vertex(self, vertex: Vertex):
        self.buffer.write(struct.pack("<fff", *vertex.position))
        self.buffer.write(struct.pack("<fff", *vertex.normals))
        self.buffer.write(struct.pack("<ff", *vertex.texture))

    def pack_links(self, vertex: Vertex):
        joints = []
        weights = []
        for id, weight in list(vertex.link.items())[:4]:
            joints.append(id)
            weights.append(weight)

        # Pad to 4
        joints.extend([0] * (4 - len(joints)))
        weights.extend([0.0] * (4 - len(weights)))

        self.buffer.write(struct.pack("<ffff", *weights))
        self.buffer.write(struct.pack("<HHHH", *joints))

    def pack_vertices(self, mesh: ModelMesh):
        for vertex in mesh.vertices:
            self.pack_vertex(vertex)
            self.pack_links(vertex)

    def pack_indices(self, mesh: ModelMesh):
        for polygon in mesh.polygons:
            self.buffer.write(struct.pack("<HHH", *polygon))

    def pack_mesh_data(self, mesh: ModelMesh) -> list[BufferViewInfo]:
        start_offset = self.buffer.tell()
        vertex_count = len(mesh.vertices)

        self.pack_vertices(mesh)

        indices_start = self.buffer.tell()
        self.pack_indices(mesh)
        indices_size = self.buffer.tell() - indices_start

        self.align_to_4bytes()

        buffer_views: list[BufferViewInfo] = []
        current_offset = start_offset

        for size in DataSize():
            buffer_views.append(
                BufferViewInfo(
                    offset=current_offset,
                    length=vertex_count * size,
                    stride=DataSize.vertex,
                    target=BufferTarget.ARRAY_BUFFER,
                )
            )
            current_offset += size

        buffer_views.append(
            BufferViewInfo(
                offset=indices_start, length=indices_size, stride=0, target=BufferTarget.ELEMENT_ARRAY_BUFFER
            )
        )

        return buffer_views

    def create_mesh_accessors(self, mesh: ModelMesh, view_index: int) -> list[AccessorInfo]:
        vertex_count = len(mesh.vertices)
        index_count = len(mesh.polygons) * 3

        return [
            AccessorInfo(
                view_index=view_index,
                count=vertex_count,
                component_type=ComponentType.FLOAT,
                attribute_type=AttributeType.VEC3,
            ),
            AccessorInfo(
                view_index=view_index + 1,
                count=vertex_count,
                component_type=ComponentType.FLOAT,
                attribute_type=AttributeType.VEC3,
            ),
            AccessorInfo(
                view_index=view_index + 2,
                count=vertex_count,
                component_type=ComponentType.FLOAT,
                attribute_type=AttributeType.VEC2,
            ),
            AccessorInfo(
                view_index=view_index + 3,
                count=vertex_count,
                component_type=ComponentType.FLOAT,
                attribute_type=AttributeType.VEC4,
            ),
            AccessorInfo(
                view_index=view_index + 4,
                count=vertex_count,
                component_type=ComponentType.UINT16,
                attribute_type=AttributeType.VEC4,
            ),
            AccessorInfo(
                view_index=view_index + 5,
                count=index_count,
                component_type=ComponentType.UINT16,
                attribute_type=AttributeType.SCALAR,
            ),
        ]
