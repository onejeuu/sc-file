from collections import defaultdict
from contextlib import contextmanager

import numpy as np

from scfile.core.context.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import Flag

from .consts import FBX


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
        self.ctx["IDS"] = defaultdict(dict)
        self.ctx["BONES"] = defaultdict(dict)
        self.ctx["MESHES"] = defaultdict(lambda: defaultdict(dict))
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
                    (b"UnitScaleFactor", b"double", b"Number", b"", 100.0),
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
            self.ctx["IDS"]["document"] = doc_id

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
            root_id = np.int64(self.ctx["IDS"]["root"])

            if self._skeleton_presented:
                with self._node(b"C", [b"OO", root_id, np.int64(0)]):
                    pass

                for bone in self.data.scene.skeleton.bones:
                    child_id = self.ctx["BONES"][bone.name]
                    parent_name = self.data.scene.skeleton.bones[bone.parent_id].name
                    parent_id = root_id if bone.is_root else self.ctx["BONES"][parent_name]

                    with self._node(b"C", [b"OO", child_id, parent_id]):
                        pass

            for mesh in self.data.scene.meshes:
                ids = self.ctx["MESHES"][mesh.name]

                with self._node(b"C", [b"OO", ids["mesh"], root_id]):
                    pass
                with self._node(b"C", [b"OO", ids["geometry"], ids["mesh"]]):
                    pass
                with self._node(b"C", [b"OO", ids["material"], ids["mesh"]]):
                    pass
                if self._skeleton_presented:
                    with self._node(b"C", [b"OO", ids["skin"], ids["geometry"]]):
                        pass

                    for global_id in mesh.bones.values():
                        cluster_id = ids.get(f"cluster_{global_id}")
                        if not cluster_id:
                            continue

                        with self._node(b"C", [b"OO", cluster_id, ids["skin"]]):
                            pass

                        bone_name = self.data.scene.skeleton.bones[global_id].name
                        bone_id = self.ctx["BONES"][bone_name]
                        with self._node(b"C", [b"OO", bone_id, cluster_id]):
                            pass

    def _write_armature(self):
        armature_id = self._next_id()
        self.ctx["IDS"]["root"] = armature_id

        root_name = b"Armature\x00\x01Model"
        with self._node(b"Model", [armature_id, root_name, b"Null"]):
            with self._node(b"Properties70"):
                with self._node(b"P", [b"InheritType", b"enum", b"", b"", 1]):
                    pass

    def _write_bone(self, bone: S.SkeletonBone):
        fbx_id = self._next_id()
        self.ctx["BONES"][bone.name] = fbx_id

        bone_name = bone.name.encode() + b"\x00\x01" + b"Model"
        with self._node(b"Model", [fbx_id, bone_name, b"LimbNode"]):
            with self._node(b"Properties70"):
                props = [
                    (b"Lcl Translation", b"Lcl Translation", b"", b"A", *bone.position.tolist()),
                    (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", *bone.rotation.tolist()),
                    (b"InheritType", b"enum", b"", b"", 1),
                ]
                for prop in props:
                    with self._node(b"P", list(prop)):
                        pass

    def _write_mesh(self, mesh: S.ModelMesh):
        fbx_id = self._next_id()
        self.ctx["MESHES"][mesh.name]["mesh"] = fbx_id

        model_name = mesh.name.encode() + b"\x00\x01" + b"Model"
        with self._node(b"Model", [fbx_id, model_name, b"Mesh"]):
            with self._node(b"Version", [232]):
                pass

            with self._node(b"Properties70"):
                props = [
                    (b"Lcl Translation", b"Lcl Translation", b"", b"A", 0.0, 0.0, 0.0),
                    (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", 0.0, 0.0, 0.0),
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

        self.ctx["MESHES"][mesh.name]["geometry"] = geom_id

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

        self.ctx["MESHES"][mesh.name]["material"] = mat_id

    def _write_mesh_skinning(self, mesh: S.ModelMesh):
        skin_id = self._next_id()
        self.ctx["MESHES"][mesh.name]["skin"] = skin_id

        skin_name = mesh.name.encode() + b"\x00\x01Deformer"
        with self._node(b"Deformer", [skin_id, skin_name, b"Skin"]):
            with self._node(b"Version", [101]):
                pass
            with self._node(b"Link_DeformAcuracy", [50.0]):
                pass

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
                with self._node(b"Version", [100]):
                    pass
                with self._node(b"Indexes", [indices]):
                    pass
                with self._node(b"Weights", [weights]):
                    pass

                mesh_transform = np.eye(4, dtype=np.float64).flatten().tolist()
                bone_transform = global_transforms[global_id].flatten().astype(np.float64).tolist()

                with self._node(b"Transform", [mesh_transform]):
                    pass
                with self._node(b"TransformLink", [bone_transform]):
                    pass

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

        if isinstance(value, (float, np.floating)):
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
