from enum import IntEnum
from typing import Any

import numpy as np

from scfile.core.context.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.flags import Flag


FBX_VERSION = 7400
FBX_HEADER = b"Kaydara FBX Binary  \x00\x1a\x00"
FBX_FILE_ID = b"\x28\xb5\x2f\xfd\x8e\xb5\x4e\x54\x9f\x38\x1e\xb9\xe6\x2b\x92\xad"


class PropertyType(IntEnum):
    INT16 = ord("Y")
    BOOL = ord("C")
    INT32 = ord("I")
    FLOAT = ord("F")
    DOUBLE = ord("D")
    INT64 = ord("L")
    STRING = ord("S")
    RAW = ord("R")
    ARRAY_DOUBLE = ord("d")
    ARRAY_INT32 = ord("i")
    ARRAY_INT64 = ord("l")
    ARRAY_FLOAT = ord("f")
    ARRAY_BOOL = ord("b")


class FbxEncoder(FileEncoder[ModelContent]):
    format = FileFormat.FBX
    order = ByteOrder.LITTLE

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self.data.flags[Flag.UV]:
            self.data.scene.flip_v_textures()

        self.ctx["NODES"] = []
        self.ctx["OBJECT_IDS"] = {}
        self.ctx["NEXT_ID"] = 0

    def serialize(self):
        self._write_header()
        self._write_top_nodes()
        self._write_footer()

    def _write_header(self):
        self.write(b"Kaydara FBX Binary  \x00\x1a\x00")
        self._writeb(F.U32, 7400)

    def _write_top_nodes(self):
        # FBXHeaderExtension
        self._start_node(b"FBXHeaderExtension")
        self._write_property(self._fbx_time(0))
        self._write_property(self._fbx_time(0))
        self._start_node(b"Creator")
        self._write_property("FBX Python Encoder")
        self._end_node()
        self._end_node()

        # GlobalSettings
        self._start_node(b"GlobalSettings")
        settings = [
            (b"UpAxis", 1),
            (b"UpAxisSign", 1),
            (b"FrontAxis", 2),
            (b"FrontAxisSign", 1),
            (b"CoordAxis", 0),
            (b"CoordAxisSign", 1),
            (b"OriginalUpAxis", 1),
            (b"OriginalUpAxisSign", 1),
            (b"UnitScaleFactor", 1.0),
            (b"OriginalUnitScaleFactor", 1.0),
            (b"TimeSpanStart", 0),
            (b"TimeSpanStop", 0),
            (b"TimeMode", 11),
        ]
        for name, value in settings:
            self._start_node(name)
            self._write_property(value)
            self._end_node()
        self._end_node()

        # Documents
        self._start_node(b"Documents")
        doc_id = self._next_id()
        self.ctx["ROOT_DOC"] = doc_id
        self._start_node(b"Document", [doc_id, b"", b"Scene"])
        self._start_node(b"Properties60")
        self._start_node(b"Property", [b"SourceFile", b"KString", b"", b""])
        self._end_node()  # Property
        self._end_node()  # Properties60
        self._start_node(b"RootNode")
        self._write_property(0)
        self._end_node()  # RootNode
        self._end_node()  # Document
        self._end_node()  # Documents

        # References
        self._start_node(b"References")
        self._end_node()

        # Definitions
        self._start_node(b"Definitions")
        self._start_node(b"Version")
        self._write_property(100)
        self._end_node()
        self._start_node(b"Count")
        self._write_property(len(self.data.scene.meshes))
        self._end_node()
        for mesh in self.data.scene.meshes:
            self._start_node(b"ObjectType", [b"Model"])
            self._start_node(b"Count")
            self._write_property(1)
            self._end_node()
            self._start_node(b"PropertyTemplate", [b"FbxNode"])
            self._start_node(b"Properties70")
            templates = [
                (b"QuaternionInterpolate", b"int", b"", 0),
                (b"Visibility", b"bool", b"A+", 1),
                (b"InheritType", b"enum", b"", 1),
            ]
            for name, type_name, flags, value in templates:
                self._start_node(b"P", [name, type_name, flags, value])
                self._end_node()
            self._end_node()  # Properties70
            self._end_node()  # PropertyTemplate
            self._end_node()  # ObjectType
        self._end_node()  # Definitions

        # Objects
        self._start_node(b"Objects")
        for mesh in self.data.scene.meshes:
            self._write_mesh(mesh)
        self._end_node()

        # Connections
        self._start_node(b"Connections")
        self._start_node(b"C", [b"OO", 0, self.ctx["ROOT_DOC"], b"RootNode"])
        self._end_node()
        for mesh in self.data.scene.meshes:
            mesh_id = self.ctx["OBJECT_IDS"][mesh.name]
            geom_id = self.ctx["OBJECT_IDS"][f"{mesh.name}_geom"]
            self._start_node(b"C", [b"OO", geom_id, mesh_id, b"Geometry"])
            self._end_node()
            self._start_node(b"C", [b"OO", mesh_id, 0, b"Model"])
            self._end_node()
        self._end_node()

    def _write_mesh(self, mesh):
        mesh_id = self._next_id()
        self.ctx["OBJECT_IDS"][mesh.name] = mesh_id

        # Model node
        self._start_node(b"Model", [mesh_id, mesh.name.encode(), b"Mesh"])
        self._start_node(b"Version")
        self._write_property(232)
        self._end_node()
        self._start_node(b"Properties70")
        props = [
            (b"GeometricTranslation", b"Lcl Translation", b"A+", (0.0, 0.0, 0.0)),
            (b"GeometricRotation", b"Lcl Rotation", b"A+", (0.0, 0.0, 0.0)),
            (b"GeometricScaling", b"Lcl Scaling", b"A+", (1.0, 1.0, 1.0)),
        ]
        for name, label, flags, value in props:
            self._start_node(b"P", [name, label, flags, value])
            self._end_node()
        self._end_node()  # Properties70
        if self.data.flags[Flag.UV]:
            self._start_node(b"MultiLayer")
            self._write_property(0)
            self._end_node()
        self._start_node(b"MultiTake")
        self._end_node()
        self._end_node()  # Model

        # Geometry node
        geom_id = self._next_id()
        self._start_node(b"Geometry", [geom_id, f"{mesh.name}Geometry".encode(), b"Mesh"])
        self._start_node(b"Version")
        self._write_property(124)
        self._end_node()
        self._start_node(b"Vertices")
        self._write_property(mesh.positions.flatten())
        self._end_node()
        self._start_node(b"PolygonVertexIndex")
        indices = self._fbx_polygon_indices(mesh.polygons)
        self._write_property(indices)
        self._end_node()
        self._start_node(b"Edges")
        self._write_property(np.array([], dtype=np.int32))
        self._end_node()
        if self.data.flags[Flag.NORMALS]:
            self._write_layer_normals(mesh)
        if self.data.flags[Flag.UV]:
            self._write_layer_uvs(mesh)
        self._write_layer_materials(mesh)
        self._end_node()  # Geometry

        self.ctx["OBJECT_IDS"][f"{mesh.name}_geom"] = geom_id

    def _write_layer_normals(self, mesh):
        self._start_node(b"LayerElementNormal", [0])
        self._start_node(b"Version")
        self._write_property(101)
        self._end_node()
        self._start_node(b"Name")
        self._write_property("")
        self._end_node()
        self._start_node(b"MappingInformationType")
        self._write_property("ByPolygonVertex")
        self._end_node()
        self._start_node(b"ReferenceInformationType")
        self._write_property("Direct")
        self._end_node()
        self._start_node(b"Normals")
        self._write_property(mesh.normals.flatten())
        self._end_node()
        self._end_node()

    def _write_layer_uvs(self, mesh):
        self._start_node(b"LayerElementUV", [0])
        self._start_node(b"Version")
        self._write_property(101)
        self._end_node()
        self._start_node(b"Name")
        self._write_property("map1")
        self._end_node()
        self._start_node(b"MappingInformationType")
        self._write_property("ByPolygonVertex")
        self._end_node()
        self._start_node(b"ReferenceInformationType")
        self._write_property("IndexToDirect")
        self._end_node()
        self._start_node(b"UV")
        self._write_property(mesh.textures.flatten())
        self._end_node()
        self._start_node(b"UVIndex")
        indices = np.arange(mesh.count.polygons * 3, dtype=np.int32)
        self._write_property(indices)
        self._end_node()
        self._end_node()

    def _write_layer_materials(self, mesh):
        self._start_node(b"LayerElementMaterial", [0])
        self._start_node(b"Version")
        self._write_property(101)
        self._end_node()
        self._start_node(b"Name")
        self._write_property("")
        self._end_node()
        self._start_node(b"MappingInformationType")
        self._write_property("AllSame")
        self._end_node()
        self._start_node(b"ReferenceInformationType")
        self._write_property("IndexToDirect")
        self._end_node()
        self._start_node(b"Materials")
        self._write_property(np.array([0], dtype=np.int32))
        self._end_node()
        self._end_node()

    def _write_footer(self):
        self._writeb(F.U32, 0)  # NULL node

    # Core node handling
    def _start_node(self, name: bytes, properties: list | None = None):
        # Save position for endOffset
        node_start = len(self.getvalue())
        self.ctx["NODES"].append({"start": node_start, "name": name})

        # Write placeholder endOffset (4 bytes)
        self._writeb(F.U32, 0)

        # Write propsNum (4 bytes)
        num_props = len(properties) if properties else 0
        self._writeb(F.U32, num_props)

        # Save position for propsLen
        props_len_pos = len(self.getvalue())

        # Write placeholder propsLen (4 bytes)
        self._writeb(F.U32, 0)

        # Write nameLen (1 byte) and name
        self._writeb(F.U8, len(name))
        self.write(name)

        # Remember where properties start
        props_start = len(self.getvalue())

        # Write properties
        if properties:
            for prop in properties:
                self._write_property(prop)

        # Calculate and write propsLen
        props_end = len(self.getvalue())
        props_size = props_end - props_start

        self.seek(props_len_pos)
        self._writeb(F.U32, props_size)
        self.seek(props_end)

    def _end_node(self):
        node = self.ctx["NODES"].pop()
        end_pos = len(self.getvalue())

        # Update endOffset
        self.seek(node["start"])
        self._writeb(F.U32, end_pos)
        self.seek(end_pos)

    # Property writers
    def _write_property(self, value):
        if isinstance(value, bool):
            self._writeb(F.U8, ord("C"))
            self._writeb(F.U8, 1 if value else 0)
            return

        if isinstance(value, int):
            if -0x8000 <= value <= 0x7FFF:
                self._writeb(F.U8, ord("Y"))
                self._writeb(F.I16, value)
            else:
                self._writeb(F.U8, ord("I"))
                self._writeb(F.I32, value)
            return

        if isinstance(value, float):
            self._writeb(F.U8, ord("D"))
            self._writeb(F.F64, value)
            return

        if isinstance(value, (bytes, str)):
            if isinstance(value, str):
                value = value.encode("utf-8")
            self._writeb(F.U8, ord("S"))
            self._writeb(F.U32, len(value))
            self.write(value)
            return

        if isinstance(value, np.ndarray):
            self._write_array_property(value)
            return

        if isinstance(value, (list, tuple)):
            self._write_array_property(np.array(value, dtype=np.float64))
            return

        raise TypeError(f"Unsupported property type: {type(value)}")

    def _write_array_property(self, arr: np.ndarray):
        if arr.dtype == np.float64:
            self._writeb(F.U8, ord("d"))
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 8)  # compressedLen
            self.write(arr.tobytes())
            return

        if arr.dtype == np.int32:
            self._writeb(F.U8, ord("i"))
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 4)  # compressedLen
            self.write(arr.tobytes())
            return

        self._write_array_property(arr.astype(np.float64))

    def _next_id(self) -> int:
        self.ctx["NEXT_ID"] += 1
        return self.ctx["NEXT_ID"]

    def _fbx_time(self, seconds: float) -> int:
        return int(seconds * 46186158000)

    def _fbx_polygon_indices(self, polygons: np.ndarray) -> np.ndarray:
        indices = polygons.flatten().astype(np.int32)
        indices[2::3] = -indices[2::3] - 1
        return indices
