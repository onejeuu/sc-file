from collections import defaultdict
from contextlib import contextmanager

import numpy as np

from scfile.core.context.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.structures import models as S
from scfile.structures.models import Flag

from .consts import DEFAULT, FBX, Props
from .io import FbxFileIO


class FbxEncoder(FileEncoder[ModelContent], FbxFileIO):
    format = FileFormat.FBX
    order = ByteOrder.LITTLE

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self.data.flags[Flag.UV]:
            self.data.scene.flip_v_textures()

        if self._skeleton_presented:
            self.data.scene.skeleton.convert_to_local()
            self.data.scene.skeleton.build_hierarchy()
            self.ctx["BINDPOSE"] = self.data.scene.skeleton.calculate_global_transforms()

        if self._animation_presented:
            self.data.scene.animation.convert_to_local(self.data.scene.skeleton)

        self.ctx["NODES"] = []
        self.ctx["CLIPS"] = []
        self.ctx["BONES"] = {}
        self.ctx["MESHES"] = defaultdict(dict)
        self.ctx["ROOT_ID"] = 0
        self.ctx["NEXT_ID"] = 0

    def serialize(self):
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
            if self._skeleton_presented:
                self._write_armature()

                for bone in self.data.scene.skeleton.bones:
                    self._write_bone(bone)

                self._write_bindpose()

                for mesh in self.data.scene.meshes:
                    self._write_mesh_skinning(mesh)

            for mesh in self.data.scene.meshes:
                self._write_mesh(mesh)

            if self._animation_presented:
                self._write_animation()

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

            if self._animation_presented:
                for clip in self.ctx.get("CLIPS", []):
                    if len(clip) == 2:
                        self._leaf(b"C", [b"OO", np.int64(clip[0]), np.int64(clip[1])])
                    else:
                        self._leaf(b"C", [b"OP", np.int64(clip[0]), np.int64(clip[1]), clip[2]])

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
            self._leaf(b"Version", [232])
            self._props70(
                [
                    (b"Lcl Translation", b"Lcl Translation", b"", b"A", *bone.position.tolist()),
                    (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", *bone.rotation.tolist()),
                    (b"RotationOrder", b"enum", b"", b"", 0),
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

    def _write_mesh_skinning(self, mesh: S.ModelMesh):
        skin_id = self._next_id()
        self.ctx["MESHES"][mesh.name]["skin"] = skin_id

        skin_name = mesh.name.encode() + b"\x00\x01Deformer"
        with self._node(b"Deformer", [skin_id, skin_name, b"Skin"]):
            self._leaf(b"Version", [101])
            self._leaf(b"Link_DeformAcuracy", [50.0])

        for global_id in mesh.bones.values():
            bone = self.data.scene.skeleton.bones[global_id]

            row_idx, col_idx = np.where(mesh.links_ids == global_id)
            if row_idx.size == 0:
                continue

            rows, inverse = np.unique(row_idx, return_inverse=True)
            weights = np.zeros(len(rows), dtype=np.float64)
            np.add.at(weights, inverse, mesh.links_weights[row_idx, col_idx])

            indices = rows.astype(np.int32)
            weights = weights.astype(np.float64)

            bindpose = self.ctx["BINDPOSE"][bone.id].astype(np.float64)
            transform = np.eye(4, dtype=np.float64).flatten().tolist()
            transform_link = bindpose.T.flatten().tolist()

            cluster_id = self._next_id()
            self.ctx["MESHES"][mesh.name][f"cluster_{global_id}"] = cluster_id

            cluster_name = bone.name.encode() + b"\x00\x01SubDeformer"
            with self._node(b"Deformer", [cluster_id, cluster_name, b"Cluster"]):
                self._leaf(b"Version", [100])
                self._leaf(b"UserData", [b"", b""])
                self._leaf(b"Indexes", [indices])
                self._leaf(b"Weights", [weights])
                self._leaf(b"Transform", [transform])
                self._leaf(b"TransformLink", [transform_link])

    def _write_bindpose(self):
        pose_id = self._next_id()

        pose_name = b"Pose\x00\x01Pose"

        bones = self.data.scene.skeleton.bones

        with self._node(b"Pose", [pose_id, pose_name, b"BindPose"]):
            self._leaf(b"Type", [b"BindPose"])
            self._leaf(b"Version", [100])
            self._leaf(b"NbPoseNodes", [len(bones) + 1])

            armature_id = self.ctx["ROOT_ID"]
            identity = np.eye(4, dtype=np.float64).flatten().tolist()
            with self._node(b"PoseNode"):
                self._leaf(b"Node", [np.int64(armature_id)])
                self._leaf(b"Matrix", [identity])

            for bone in bones:
                bone_id = self.ctx["BONES"][bone.name]
                matrix = self.ctx["BINDPOSE"][bone.id].T.flatten().astype(np.float64).tolist()
                with self._node(b"PoseNode"):
                    self._leaf(b"Node", [np.int64(bone_id)])
                    self._leaf(b"Matrix", [matrix])

    def _write_animation(self):
        for clip in self.data.scene.animation.clips:
            stack_id = self._next_id()
            stack_name = clip.name.encode() + b"\x00\x01AnimationStack"
            with self._node(b"AnimationStack", [stack_id, stack_name, b""]):
                self._leaf(b"Properties70", [])

            layer_id = self._next_id()
            layer_name = b"BaseLayer\x00\x01AnimationLayer"
            self._leaf(b"AnimationLayer", [layer_id, layer_name, b""])

            self.ctx["CLIPS"].append((layer_id, stack_id))

            times = (clip.times * 46186158000).astype(np.int64)
            flags = np.full(len(times), 0x218, dtype=np.int32)
            attr_data = np.zeros(4, dtype=np.float32)
            attr_count = np.array([len(times)], dtype=np.int32)

            for bone in self.data.scene.skeleton.bones:
                transforms = clip.transforms[:, bone.id, :]
                rotations = transforms[:, 0:3].astype(np.float32)
                translations = transforms[:, 4:7].astype(np.float32)

                bone_id = self.ctx["BONES"][bone.name]

                t_node_id = self._next_id()
                t_node_name = b"T\x00\x01AnimationCurveNode"
                with self._node(b"AnimationCurveNode", [t_node_id, t_node_name, b""]):
                    self._props70(DEFAULT.CURVE)

                r_node_id = self._next_id()
                r_node_name = b"R\x00\x01AnimationCurveNode"
                with self._node(b"AnimationCurveNode", [r_node_id, r_node_name, b""]):
                    self._props70(DEFAULT.CURVE)

                for i, axis in enumerate([b"d|X", b"d|Y", b"d|Z"]):
                    curve_id = self._next_id()
                    with self._node(b"AnimationCurve", [curve_id, b"\x00\x01AnimationCurve", b""]):
                        self._leaf(b"Default", [0.0])
                        self._leaf(b"KeyVer", [4008])
                        self._leaf(b"KeyTime", [times])
                        self._leaf(b"KeyValueFloat", [translations[:, i]])
                        self._leaf(b"KeyAttrFlags", [flags])
                        self._leaf(b"KeyAttrDataFloat", [attr_data])
                        self._leaf(b"KeyAttrRefCount", [attr_count])
                    self.ctx["CLIPS"].append((curve_id, t_node_id, axis))

                for i, axis in enumerate([b"d|X", b"d|Y", b"d|Z"]):
                    curve_id = self._next_id()
                    with self._node(b"AnimationCurve", [curve_id, b"\x00\x01AnimationCurve", b""]):
                        self._leaf(b"Default", [0.0])
                        self._leaf(b"KeyVer", [4008])
                        self._leaf(b"KeyTime", [times])
                        self._leaf(b"KeyValueFloat", [rotations[:, i]])
                        self._leaf(b"KeyAttrFlags", [flags])
                        self._leaf(b"KeyAttrDataFloat", [attr_data])
                        self._leaf(b"KeyAttrRefCount", [attr_count])
                    self.ctx["CLIPS"].append((curve_id, r_node_id, axis))

                self.ctx["CLIPS"].append((t_node_id, bone_id, b"Lcl Translation"))
                self.ctx["CLIPS"].append((r_node_id, bone_id, b"Lcl Rotation"))
                self.ctx["CLIPS"].append((layer_id, t_node_id))
                self.ctx["CLIPS"].append((layer_id, r_node_id))

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
