from collections import defaultdict
from contextlib import contextmanager

import numpy as np

from scfile.core.context.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import Flag

from .consts import DEFAULT, FBX, Props
from .enums import PropertyType


class FbxEncoder(FileEncoder[ModelContent]):
    format = FileFormat.FBX
    order = ByteOrder.LITTLE

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self._skeleton_presented:
            self.data.scene.skeleton.convert_to_local()
            self.data.scene.skeleton.build_hierarchy()

        if self.data.flags[Flag.UV]:
            self.data.scene.flip_v_textures()

        self.ctx["NODES"] = []
        self.ctx["BONES"] = defaultdict(dict)
        self.ctx["MESHES"] = defaultdict(lambda: defaultdict(dict))
        self.ctx["ROOT_ID"] = 0
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
            if self._skeleton_presented:
                self._write_armature()

                for bone in self.data.scene.skeleton.bones:
                    self._write_bone(bone)

                for mesh in self.data.scene.meshes:
                    self._write_mesh_skinning(mesh)

            for mesh in self.data.scene.meshes:
                self._write_mesh(mesh)

        # Connections
        with self._node(b"Connections", root=True):
            root_id = np.int64(self.ctx["ROOT_ID"])

            if self._skeleton_presented:
                self._leaf(b"C", [b"OO", root_id, np.int64(0)])

                for bone in self.data.scene.skeleton.bones:
                    child_id = self.ctx["BONES"][bone.name]
                    parent_name = self.data.scene.skeleton.bones[bone.parent_id].name
                    parent_id = root_id if bone.is_root else self.ctx["BONES"][parent_name]

                    self._leaf(b"C", [b"OO", child_id, parent_id])

            for mesh in self.data.scene.meshes:
                ids = self.ctx["MESHES"][mesh.name]

                self._leaf(b"C", [b"OO", ids["mesh"], root_id])
                self._leaf(b"C", [b"OO", ids["geometry"], ids["mesh"]])
                self._leaf(b"C", [b"OO", ids["material"], ids["mesh"]])

                if self._skeleton_presented:
                    self._leaf(b"C", [b"OO", ids["skin"], ids["geometry"]])

                    for global_id in mesh.bones.values():
                        cluster_id = ids.get(f"cluster_{global_id}")
                        if not cluster_id:
                            continue

                        bone_name = self.data.scene.skeleton.bones[global_id].name
                        bone_id = self.ctx["BONES"][bone_name]

                        self._leaf(b"C", [b"OO", cluster_id, ids["skin"]])
                        self._leaf(b"C", [b"OO", bone_id, cluster_id])

    def _write_armature(self):
        armature_id = self._next_id()
        self.ctx["ROOT_ID"] = armature_id

        root_name = b"Armature\x00\x01Model"
        with self._node(b"Model", [armature_id, root_name, b"Null"]):
            self._props70([(b"InheritType", b"enum", b"", b"", 1)])

    def _write_bone(self, bone: S.SkeletonBone):
        fbx_id = self._next_id()
        self.ctx["BONES"][bone.name] = fbx_id

        bone_name = bone.name.encode() + b"\x00\x01" + b"Model"
        with self._node(b"Model", [fbx_id, bone_name, b"LimbNode"]):
            self._props70(
                [
                    (b"Lcl Translation", b"Lcl Translation", b"", b"A", *bone.position.tolist()),
                    (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", *bone.rotation.tolist()),
                    (b"InheritType", b"enum", b"", b"", 1),
                ]
            )

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
            self._leaf(b"Vertices", [mesh.positions.flatten().astype(np.float64)])
            self._leaf(b"PolygonVertexIndex", [self._fbx_polygon_indices(mesh.polygons)])
            self._leaf(b"Edges", [])

            with self._node(b"LayerElementMaterial", [0]):
                self._leaf(b"Version", [101])
                self._leaf(b"Name", [b""])
                self._leaf(b"MappingInformationType", [b"AllSame"])
                self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                self._leaf(b"Materials", [np.array([0], dtype=np.int32)])

            if self.data.flags[Flag.NORMALS]:
                with self._node(b"LayerElementNormal", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b""])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"Normals", [mesh.normals.flatten().astype(np.float64)])
                    self._leaf(b"NormalsIndex", [indexes])

            if self.data.flags[Flag.UV]:
                with self._node(b"LayerElementUV", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b"UVMap"])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"UV", [mesh.uv1.flatten().astype(np.float64)])
                    self._leaf(b"UVIndex", [indexes])

            with self._node(b"Layer", [0]):
                self._leaf(b"Version", [100])

                with self._node(b"LayerElement", []):
                    self._leaf(b"Type", [b"Material"])
                    self._leaf(b"TypedIndex", [0])

                if self.data.flags[Flag.NORMALS]:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"Normal"])
                        self._leaf(b"TypedIndex", [0])

                if self.data.flags[Flag.UV]:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"UV"])
                        self._leaf(b"TypedIndex", [0])

        self.ctx["MESHES"][mesh.name]["geometry"] = geom_id

        mat_id = self._next_id()
        material_name = mesh.material.encode() + b"\x00\x01" + b"Material"
        with self._node(b"Material", [mat_id, material_name, b""]):
            self._leaf(b"Version", [102])
            self._props70(DEFAULT.MATERIAL)

        self.ctx["MESHES"][mesh.name]["material"] = mat_id

    def _write_mesh_skinning(self, mesh: S.ModelMesh):
        skin_id = self._next_id()
        self.ctx["MESHES"][mesh.name]["skin"] = skin_id

        skin_name = mesh.name.encode() + b"\x00\x01Deformer"
        with self._node(b"Deformer", [skin_id, skin_name, b"Skin"]):
            self._leaf(b"Version", [101])
            self._leaf(b"Link_DeformAcuracy", [50.0])

        global_transforms = self.data.scene.skeleton.calculate_global_transforms()

        for local_id, global_id in mesh.bones.items():
            bone = self.data.scene.skeleton.bones[global_id]

            row_idx, col_idx = np.where(mesh.links_ids == local_id)

            if row_idx.size == 0:
                continue

            indices = row_idx.astype(np.int32)
            weights = mesh.links_weights[row_idx, col_idx].astype(np.float64)

            cluster_id = self._next_id()
            self.ctx["MESHES"][mesh.name][f"cluster_{global_id}"] = cluster_id

            cluster_name = bone.name.encode() + b"\x00\x01SubDeformer"
            with self._node(b"Deformer", [cluster_id, cluster_name, b"Cluster"]):
                self._leaf(b"Version", [100])
                self._leaf(b"Indexes", [indices])
                self._leaf(b"Weights", [weights])

                mesh_transform = np.eye(4, dtype=np.float64).flatten().tolist()
                bone_transform = global_transforms[global_id].flatten().astype(np.float64).tolist()

                self._leaf(b"Transform", [mesh_transform])
                self._leaf(b"TransformLink", [bone_transform])

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

        end_pos = len(self.getvalue())

        # Update node header
        self.seek(node["start"])
        self._writeb(F.U32, end_pos)
        self._writeb(F.U32, node["prop_count"])
        self._writeb(F.U32, node["prop_len"])
        self.seek(end_pos)

    # Property writers
    # TODO: move to IO
    def _write_property(self, value):
        if isinstance(value, bool):
            self._writeb(F.U8, PropertyType.BOOL)
            self._writeb(F.U8, 1 if value else 0)
            return

        if isinstance(value, int):
            self._writeb(F.U8, PropertyType.INT32)
            self._writeb(F.I32, value)
            return

        if isinstance(value, np.integer):
            self._writeb(F.U8, PropertyType.INT64)
            self._writeb(F.I64, int(value))
            return

        if isinstance(value, (float, np.floating)):
            self._writeb(F.U8, PropertyType.DOUBLE)
            self._writeb(F.F64, value)
            return

        if isinstance(value, (bytes, str)):
            if isinstance(value, str):
                value = value.encode("utf-8")
            self._writeb(F.U8, PropertyType.STRING)
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

    # TODO: move to IO
    def _write_array_property(self, arr: np.ndarray):
        if arr.dtype == np.float64:
            self._writeb(F.U8, PropertyType.ARRAY_DOUBLE)
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 8)  # compressedLen
            self.write(arr.tobytes())
            return

        if arr.dtype == np.int32:
            self._writeb(F.U8, PropertyType.ARRAY_INT32)
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 4)  # compressedLen
            self.write(arr.tobytes())
            return

        self._write_array_property(arr.astype(np.float64))

    def _next_id(self) -> np.int64:
        self.ctx["NEXT_ID"] += 1
        return np.int64(self.ctx["NEXT_ID"])

    # TODO: move to IO
    def _fbx_time(self, seconds: float) -> int:
        return int(seconds * 46186158000)

    def _fbx_polygon_indices(self, polygons: np.ndarray) -> np.ndarray:
        indices = polygons.flatten().astype(np.int32)
        indices[2::3] = -indices[2::3] - 1
        return indices
