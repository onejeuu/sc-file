from contextlib import contextmanager
from enum import IntEnum

import numpy as np

from scfile import __version__
from scfile.core.context.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures.flags import Flag
from scfile.structures.mesh import ModelMesh


class FBX:
    VERSION = 7400
    HEADER_VERSION = 1003
    HEADER = b"Kaydara FBX Binary  \x00\x1a\x00"
    FILE_ID = b"\x28\xb5\x2f\xfd\x8e\xb5\x4e\x54\x9f\x38\x1e\xb9\xe6\x2b\x92\xad"
    NULL_NODE = b"\x00" * 13
    CREATOR = b"onejeuu/sc-file v" + __version__.encode()


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
        self.write(FBX.NULL_NODE)

    def _write_header(self):
        self.write(FBX.HEADER)
        self._writeb(F.U32, FBX.VERSION)

    def _write_top_nodes(self):
        # FBX Header Extension
        with self._node(b"FBXHeaderExtension", root=True):
            with self._node(b"FBXHeaderVersion", [FBX.HEADER_VERSION]):
                pass
            with self._node(b"FBXVersion", [FBX.VERSION]):
                pass
            with self._node(b"Creator", [FBX.CREATOR]):
                pass

        # Global Settings
        with self._node(b"GlobalSettings", root=True):
            with self._node(b"Version", [1000]):
                pass
            with self._node(b"Properties70"):
                settings = [
                    (b"UpAxis", b"int", b"Integer", b"", 1),
                    (b"UpAxisSign", b"int", b"Integer", b"", 1),
                    (b"FrontAxis", b"int", b"Integer", b"", 2),
                    (b"FrontAxisSign", b"int", b"Integer", b"", 1),
                    (b"CoordAxis", b"int", b"Integer", b"", 0),
                    (b"CoordAxisSign", b"int", b"Integer", b"", 1),
                    (b"UnitScaleFactor", b"double", b"Number", b"", 1.0),
                    (b"TimeMode", b"enum", b"", b"", 11),
                    (b"TimeSpanStart", b"KTime", b"Time", b"", 0),
                    (b"TimeSpanStop", b"KTime", b"Time", b"", 0),
                ]
                for props in settings:
                    with self._node(b"P", list(props)):
                        pass

        # Documents
        with self._node(b"Documents", root=True):
            doc_id = self._next_id()
            self.ctx["ROOT_DOC"] = doc_id

            with self._node(b"Count", [1]):
                pass
            with self._node(b"Document", [doc_id, b"Scene", b"Scene"]):
                with self._node(b"Properties70"):
                    with self._node(b"P", [b"SourceObject", b"object", b"", b""]):
                        pass

                with self._node(b"RootNode", [0]):
                    pass

        # References
        with self._node(b"References", root=True):
            pass

        # Definitions
        with self._node(b"Definitions", root=True):
            with self._node(b"Version", [100]):
                pass

            with self._node(b"Count", [len(self.data.scene.meshes)]):
                pass

            for mesh in self.data.scene.meshes:
                with self._node(b"ObjectType", [b"Model"]):
                    with self._node(b"Count", [1]):
                        pass

                    with self._node(b"PropertyTemplate", [b"FbxNode"]):
                        with self._node(b"Properties70"):
                            props = [
                                (b"Visibility", b"Visibility", b"", b"A", 1.0),
                            ]
                            for prop in props:
                                with self._node(b"P", list(prop)):
                                    pass

        # Objects
        with self._node(b"Objects", root=True):
            for mesh in self.data.scene.meshes:
                self._write_mesh(mesh)

        # Connections
        with self._node(b"Connections", root=True):
            for mesh in self.data.scene.meshes:
                mesh_id = self.ctx["OBJECT_IDS"][mesh.name]
                geom_id = self.ctx["OBJECT_IDS"][f"{mesh.name}_geom"]
                mat_id = self.ctx["OBJECT_IDS"][f"{mesh.name}_mat"]
                with self._node(b"C", [b"OO", mesh_id, np.int64(0)]):
                    pass
                with self._node(b"C", [b"OO", geom_id, mesh_id]):
                    pass
                with self._node(b"C", [b"OO", mat_id, mesh_id]):
                    pass

    def _write_mesh(self, mesh: ModelMesh):
        mesh_id = self._next_id()
        self.ctx["OBJECT_IDS"][mesh.name] = mesh_id

        model_name = mesh.name.encode() + b"\x00\x01" + b"Model"
        with self._node(b"Model", [mesh_id, model_name, b"Mesh"]):
            with self._node(b"Version", [232]):
                pass

            with self._node(b"Properties70"):
                # TODO: scaling size
                props = [
                    (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", 0.0, 0.0, 0.0),
                    (b"Lcl Scaling", b"Lcl Scaling", b"", b"A", 100.0, 100.0, 100.0),
                    (b"DefaultAttributeIndex", b"int", b"Integer", b"", 0),
                    (b"InheritType", b"enum", b"", b"", 1),
                ]
                for prop in props:
                    with self._node(b"P", list(prop)):
                        pass

            with self._node(b"MultiTake", [0]):
                pass

            if self.data.flags[Flag.UV]:
                with self._node(b"MultiLayer", [0]):
                    pass

        # Geometry node
        geom_id = self._next_id()
        geometry_name = mesh.name.encode() + b"\x00\x01" + b"Geometry"

        indexes = mesh.polygons.flatten().astype(np.int32)

        with self._node(b"Geometry", [geom_id, geometry_name, b"Mesh"]):
            with self._node(b"Properties70"):
                pass
            with self._node(b"GeometryVersion", [124]):
                pass
            with self._node(b"Vertices", [mesh.positions.flatten().astype(np.float64)]):
                pass
            with self._node(b"PolygonVertexIndex", [self._fbx_polygon_indices(mesh.polygons)]):
                pass
            with self._node(b"Edges", []):
                pass

            with self._node(b"LayerElementMaterial", [0]):
                with self._node(b"Version", [101]):
                    pass
                with self._node(b"Name", [b""]):
                    pass
                with self._node(b"MappingInformationType", [b"AllSame"]):
                    pass
                with self._node(b"ReferenceInformationType", [b"IndexToDirect"]):
                    pass
                with self._node(b"Materials", [np.array([0], dtype=np.int32)]):
                    pass

            if self.data.flags[Flag.NORMALS]:
                with self._node(b"LayerElementNormal", [0]):
                    with self._node(b"Version", [101]):
                        pass
                    with self._node(b"Name", [b""]):
                        pass
                    with self._node(b"MappingInformationType", [b"ByPolygonVertex"]):
                        pass
                    with self._node(b"ReferenceInformationType", [b"IndexToDirect"]):
                        pass
                    with self._node(b"Normals", [mesh.normals.flatten().astype(np.float64)]):
                        pass
                    with self._node(b"NormalsIndex", [indexes]):
                        pass

            if self.data.flags[Flag.UV]:
                with self._node(b"LayerElementUV", [0]):
                    with self._node(b"Version", [101]):
                        pass
                    with self._node(b"Name", [b"UVMap"]):
                        pass
                    with self._node(b"MappingInformationType", [b"ByPolygonVertex"]):
                        pass
                    with self._node(b"ReferenceInformationType", [b"IndexToDirect"]):
                        pass
                    with self._node(b"UV", [mesh.uv1.flatten().astype(np.float64)]):
                        pass
                    with self._node(b"UVIndex", [indexes]):
                        pass

            with self._node(b"Layer", [0]):
                with self._node(b"Version", [100]):
                    pass

                with self._node(b"LayerElement", []):
                    with self._node(b"Type", [b"Material"]):
                        pass
                    with self._node(b"TypedIndex", [0]):
                        pass

                if self.data.flags[Flag.NORMALS]:
                    with self._node(b"LayerElement", []):
                        with self._node(b"Type", [b"Normal"]):
                            pass
                        with self._node(b"TypedIndex", [0]):
                            pass

                if self.data.flags[Flag.UV]:
                    with self._node(b"LayerElement", []):
                        with self._node(b"Type", [b"UV"]):
                            pass
                        with self._node(b"TypedIndex", [0]):
                            pass

        self.ctx["OBJECT_IDS"][f"{mesh.name}_geom"] = geom_id

        mat_id = self._next_id()
        material_name = mesh.material.encode() + b"\x00\x01" + b"Material"
        with self._node(b"Material", [mat_id, material_name, b""]):
            with self._node(b"Version", [102]):
                pass
            with self._node(b"Properties70"):
                props = [
                    (b"DiffuseColor", b"Color", b"", b"A", 0.8, 0.8, 0.8),
                    (b"EmissiveColor", b"Color", b"", b"A", 1.0, 1.0, 1.0),
                    (b"EmissiveFactor", b"Number", b"", b"A", 0.0),
                    (b"AmbientColor", b"Color", b"", b"A", 0.05, 0.05, 0.05),
                    (b"AmbientFactor", b"Number", b"", b"A", 0.0),
                    (b"BumpFactor", b"double", b"Number", b"", 0.0),
                    (b"SpecularColor", b"Color", b"", b"A", 0.8, 0.8, 0.8),
                    (b"SpecularFactor", b"Number", b"", b"A", 0.0),
                    (b"Shininess", b"Number", b"", b"A", 0.0),
                    (b"ShininessExponent", b"Number", b"", b"A", 0.0),
                    (b"ReflectionColor", b"Color", b"", b"A", 0.8, 0.8, 0.8),
                    (b"ReflectionFactor", b"Number", b"", b"A", 0.0),
                ]
                for prop in props:
                    with self._node(b"P", list(prop)):
                        pass

        self.ctx["OBJECT_IDS"][f"{mesh.name}_mat"] = mat_id

    @contextmanager
    def _node(self, name: bytes, properties: list | None = None, root: bool = False):
        if self.ctx["NODES"]:
            self.ctx["NODES"][-1]["children"] = True

        self._start_node(name, properties, root)

        try:
            yield
        finally:
            self._end_node()

    def _start_node(self, name: bytes, properties: list | None = None, root: bool = False):
        properties = properties or []
        node_start = len(self.getvalue())

        # Placeholder header
        self._writeb(F.U32, 0)  # endOffset
        self._writeb(F.U32, 0)  # numProperties
        self._writeb(F.U32, 0)  # propertyListLen
        self._writeb(F.U8, len(name))
        self.write(name)

        # Properties
        props_start = len(self.getvalue())
        prop_count = 0
        for prop in properties:
            self._write_property(prop)
            prop_count += 1

        prop_len = len(self.getvalue()) - props_start

        self.ctx["NODES"].append(
            dict(start=node_start, prop_count=prop_count, prop_len=prop_len, root=root, children=False)
        )

    def _end_node(self):
        node = self.ctx["NODES"].pop()

        if node["root"] or node["children"]:
            self.write(FBX.NULL_NODE)

        end_pos = len(self.getvalue())

        # Update node header
        self.seek(node["start"])
        self._writeb(F.U32, end_pos)
        self._writeb(F.U32, node["prop_count"])
        self._writeb(F.U32, node["prop_len"])
        self.seek(end_pos)

    # Property writers
    def _write_property(self, value):
        if isinstance(value, bool):
            self._writeb(F.U8, ord("C"))
            self._writeb(F.U8, 1 if value else 0)
            return

        if isinstance(value, int):
            self._writeb(F.U8, ord("I"))
            self._writeb(F.I32, value)
            return

        if isinstance(value, np.integer):
            self._writeb(F.U8, ord("L"))
            self._writeb(F.I64, int(value))
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

        if isinstance(value, list):
            self._write_array_property(np.array(value, dtype=np.float64))
            return

        raise TypeError(f"Unsupported property type: {type(value)}!!!")

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

    def _next_id(self) -> np.int64:
        self.ctx["NEXT_ID"] += 1
        return np.int64(self.ctx["NEXT_ID"])

    def _fbx_time(self, seconds: float) -> int:
        return int(seconds * 46186158000)

    def _fbx_polygon_indices(self, polygons: np.ndarray) -> np.ndarray:
        indices = polygons.flatten().astype(np.int32)
        indices[2::3] = -indices[2::3] - 1
        return indices
