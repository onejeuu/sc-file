from collections import defaultdict
from contextlib import contextmanager

import numpy as np

from scfile.core import FileEncoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import Flag
from scfile.structures.models import transforms as T

from .consts import DEFAULT, FBX, Props
from .io import FbxFileIO


class FbxEncoder(FileEncoder[ModelContent], FbxFileIO):
    format = FileFormat.FBX
    order = ByteOrder.LITTLE

    transforms = [T.unique_names, T.flip_uv]

    def serialize(self):
        self.ctx["NODES"] = []
        self.ctx["CLIPS"] = []
        self.ctx["BONES"] = {}
        self.ctx["MESHES"] = defaultdict(dict)
        self.ctx["ROOT_ID"] = 0
        self.ctx["NEXT_ID"] = 0

        self._write_header()
        self._write_nodes()
        self.write(FBX.NULL_NODE)

    def _write_header(self):
        self.write(FBX.HEADER)
        self._writeb(F.U32, FBX.VERSION)

    def _write_nodes(self):
        # FBX Header Extension
        with self._node(b"FBXHeaderExtension", root=True):
            self._leaf(b"FBXHeaderVersion", [FBX.HEADER_VERSION])
            self._leaf(b"FBXVersion", [FBX.VERSION])
            self._leaf(b"Creator", [FBX.CREATOR])

        # Global Settings
        with self._node(b"GlobalSettings", root=True):
            self._leaf(b"Version", [1000])
            self._props70(DEFAULT.SETTINGS)

        # Documents
        with self._node(b"Documents", root=True):
            doc_id = self._next_id()

            self._leaf(b"Count", [1])

            with self._node(b"Document", [doc_id, b"Scene", b"Scene"]):
                self._props70([(b"SourceObject", b"object", b"", b"")])
                self._leaf(b"RootNode", [0])

        # References
        with self._node(b"References", root=True):
            pass

        # Definitions
        with self._node(b"Definitions", root=True):
            self._leaf(b"Version", [100])
            self._leaf(b"Count", [len(self.data.scene.meshes)])

            for mesh in self.data.scene.meshes:
                with self._node(b"ObjectType", [b"Model"]):
                    self._leaf(b"Count", [1])

                    with self._node(b"PropertyTemplate", [b"FbxNode"]):
                        self._props70([(b"Visibility", b"Visibility", b"", b"A", 1.0)])

        # Objects
        with self._node(b"Objects", root=True):
            for mesh in self.data.scene.meshes:
                self._write_mesh(mesh)

        # Connections
        with self._node(b"Connections", root=True):
            root_id = np.int64(self.ctx["ROOT_ID"])

            for mesh in self.data.scene.meshes:
                ids = self.ctx["MESHES"][mesh.name]
                self._leaf(b"C", [b"OO", ids["mesh"], root_id])
                self._leaf(b"C", [b"OO", ids["geometry"], ids["mesh"]])
                self._leaf(b"C", [b"OO", ids["material"], ids["mesh"]])

    def _write_mesh(self, mesh: S.ModelMesh):
        fbx_id = self._next_id()
        self.ctx["MESHES"][mesh.name]["mesh"] = fbx_id

        model_name = mesh.name.encode() + b"\x00\x01" + b"Model"
        with self._node(b"Model", [fbx_id, model_name, b"Mesh"]):
            self._leaf(b"Version", [232])
            self._leaf(b"MultiTake", [0])
            self._leaf(b"MultiLayer", [0])
            self._props70(DEFAULT.MESH)

        # Geometry node
        geom_id = self._next_id()
        geometry_name = mesh.name.encode() + b"\x00\x01" + b"Geometry"

        indexes = mesh.polygons.flatten().astype(np.int32)

        with self._node(b"Geometry", [geom_id, geometry_name, b"Mesh"]):
            self._leaf(b"Properties70")
            self._leaf(b"GeometryVersion", [124])
            self._leaf(b"Vertices", [mesh.vertices.flatten().astype(np.float64)])
            self._leaf(b"PolygonVertexIndex", [self._fbx_polygon_indices(mesh.polygons)])
            self._leaf(b"Edges", [])

            with self._node(b"LayerElementMaterial", [0]):
                self._leaf(b"Version", [101])
                self._leaf(b"Name", [b""])
                self._leaf(b"MappingInformationType", [b"AllSame"])
                self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                self._leaf(b"Materials", [np.array([0], dtype=np.int32)])

            if self.data.flags[Flag.UV]:
                with self._node(b"LayerElementUV", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b"UVMap"])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"UV", [mesh.uv1.flatten().astype(np.float64)])
                    self._leaf(b"UVIndex", [indexes])

            if self.data.flags[Flag.UV2]:
                with self._node(b"LayerElementUV", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b"UVMap_2"])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"UV", [mesh.uv2.flatten().astype(np.float64)])
                    self._leaf(b"UVIndex", [indexes])

            if self.data.flags[Flag.NORMALS]:
                with self._node(b"LayerElementNormal", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b""])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"Normals", [mesh.normals.flatten().astype(np.float64)])
                    self._leaf(b"NormalsIndex", [indexes])

            with self._node(b"Layer", [0]):
                self._leaf(b"Version", [100])

                with self._node(b"LayerElement", []):
                    self._leaf(b"Type", [b"Material"])
                    self._leaf(b"TypedIndex", [0])

                if self.data.flags[Flag.UV]:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"UV"])
                        self._leaf(b"TypedIndex", [0])

                if self.data.flags[Flag.UV2]:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"UV"])
                        self._leaf(b"TypedIndex", [1])

                if self.data.flags[Flag.NORMALS]:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"Normal"])
                        self._leaf(b"TypedIndex", [0])

        self.ctx["MESHES"][mesh.name]["geometry"] = geom_id

        mat_id = self._next_id()
        material_name = mesh.material.encode() + b"\x00\x01" + b"Material"
        with self._node(b"Material", [mat_id, material_name, b""]):
            self._leaf(b"Version", [102])
            self._props70(DEFAULT.MATERIAL)

        self.ctx["MESHES"][mesh.name]["material"] = mat_id

    @contextmanager
    def _node(self, name: bytes, properties: list | None = None, root: bool = False):
        if self.ctx["NODES"]:
            self.ctx["NODES"][-1]["children"] = True

        self._start_node(name, properties, root)

        try:
            yield
        finally:
            self._end_node()

    def _leaf(self, name: bytes, properties: list | None = None, root: bool = False):
        with self._node(name=name, properties=properties, root=root):
            pass

    def _props70(self, props: Props):
        with self._node(b"Properties70"):
            for prop in props:
                with self._node(b"P", list(prop)):
                    pass

    def _start_node(self, name: bytes, properties: list | None = None, root: bool = False):
        properties = properties or []
        node_start = self.tell()

        # Placeholder header
        self._writeb(F.U32, 0)  # endOffset
        self._writeb(F.U32, 0)  # numProperties
        self._writeb(F.U32, 0)  # propertyListLen
        self._writeb(F.U8, len(name))
        self.write(name)

        # Properties
        props_start = self.tell()
        prop_count = 0
        for prop in properties:
            self._write_property(prop)
            prop_count += 1

        prop_len = self.tell() - props_start

        self.ctx["NODES"].append(
            dict(
                start=node_start,
                prop_count=prop_count,
                prop_len=prop_len,
                root=root,
                children=False,
            )
        )

    def _end_node(self):
        node = self.ctx["NODES"].pop()

        if node["root"] or node["children"]:
            self.write(FBX.NULL_NODE)

        end_pos = self.tell()

        # Update node header
        self.seek(node["start"])
        self._writeb(F.U32, end_pos)
        self._writeb(F.U32, node["prop_count"])
        self._writeb(F.U32, node["prop_len"])
        self.seek(end_pos)

    def _next_id(self) -> np.int64:
        self.ctx["NEXT_ID"] += 1
        return np.int64(self.ctx["NEXT_ID"])

    def _fbx_polygon_indices(self, polygons: np.ndarray) -> np.ndarray:
        indices = polygons.flatten().astype(np.int32)
        indices[2::3] = -indices[2::3] - 1
        return indices
