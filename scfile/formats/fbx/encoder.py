from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from typing import override

import numpy as np

from scfile.core import ModelEncoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.io.fbx import Cluster, FbxWriter
from scfile.structures import models as S
from scfile.structures.models import Feature
from scfile.structures.models import transforms as T

from .consts import DEFAULT, FBX, Props


type Skinning = dict[int, Cluster]
type Curves = tuple[tuple[bytes, np.int64], ...]
type CurveNode = tuple[np.int64, Curves]


@dataclass(slots=True)
class AnimationNodes:
    stack: np.int64
    layer: np.int64
    translations: list[CurveNode | None]
    rotations: list[CurveNode | None]


class FbxEncoder(ModelEncoder[FbxWriter]):
    format = FileFormat.FBX
    order = ByteOrder.LITTLE

    io_factory = FbxWriter

    features = (
        Feature.UV,
        Feature.UV2,
        Feature.NORMALS,
        Feature.SKELETON,
        Feature.BONE_ANIMATION,
    )
    transforms = T.scene_transforms(
        T.unique_names,
        T.flip_uv,
        T.skeleton_to_local,
        T.animation_to_absolute,
    )

    @override
    def _serialize(self):
        self._prepare()
        self._write_header()
        self._write_nodes()
        self.io.write(FBX.NULL_NODE)

    def _prepare(self):
        self._ctx["NODES"] = []
        self._ctx["BONES"] = {}
        self._ctx["MESHES"] = defaultdict(dict)
        self._ctx["ROOT_ID"] = 0
        self._ctx["NEXT_ID"] = 0
        self._ctx["SKELETON"] = self.includes(Feature.SKELETON) and bool(self.data.scene.skeleton.bones)
        self._ctx["ANIMATION"] = self.includes(Feature.BONE_ANIMATION)
        self._ctx["SKINNING"] = (
            {mesh.name: self._mesh_skinning(mesh) for mesh in self.data.scene.meshes} if self._ctx["SKELETON"] else {}
        )
        self._ctx["ANIMATIONS"] = []
        self._ctx["ROTATIONS"] = (
            [S.quaternions_to_euler(clip.rotations) for clip in self.data.scene.animation.clips]
            if self._ctx["ANIMATION"]
            else []
        )

        if self._ctx["SKELETON"]:
            self._ctx["BIND_POSE"] = T.global_transforms(self.data.scene.skeleton)

    def _write_header(self):
        self.io.write(FBX.HEADER)
        self.io.value(F.U32, FBX.VERSION)

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
            self._write_definitions()

        # Objects
        with self._node(b"Objects", root=True):
            if self._ctx["SKELETON"]:
                self._write_armature()
                self._write_bones()

            for mesh in self.data.scene.meshes:
                self._write_mesh(mesh)

            if self._ctx["SKELETON"]:
                self._write_bind_pose()
                for mesh in self.data.scene.meshes:
                    self._write_skinning(mesh)

            if self._ctx["ANIMATION"]:
                self._write_animations()

        # Connections
        with self._node(b"Connections", root=True):
            root_id = np.int64(self._ctx["ROOT_ID"])

            if self._ctx["SKELETON"]:
                self._leaf(b"C", [b"OO", root_id, np.int64(0)])
                self._write_bone_connections(root_id)

            for mesh in self.data.scene.meshes:
                ids = self._ctx["MESHES"][mesh.name]
                self._leaf(b"C", [b"OO", ids["mesh"], np.int64(0)])
                self._leaf(b"C", [b"OO", ids["geometry"], ids["mesh"]])
                self._leaf(b"C", [b"OO", ids["material"], ids["mesh"]])

                if "skin" in ids:
                    self._leaf(b"C", [b"OO", ids["skin"], ids["geometry"]])
                    self._write_cluster_connections(mesh, ids)

            if self._ctx["ANIMATION"]:
                self._write_animation_connections()

    def _write_definitions(self):
        meshes = len(self.data.scene.meshes)
        bones = len(self.data.scene.skeleton.bones) if self._ctx["SKELETON"] else 0
        skins = sum(bool(skinning) for skinning in self._ctx["SKINNING"].values())
        clusters = sum(len(skinning) for skinning in self._ctx["SKINNING"].values())
        models = meshes + bones + bool(bones)

        definitions = [(b"Model", models), (b"Geometry", meshes), (b"Material", meshes)]
        if skins:
            definitions.append((b"Deformer", skins + clusters))

        if bones:
            definitions.append((b"Pose", 1))
        if self._ctx["ANIMATION"]:
            clips = len(self.data.scene.animation.clips)
            nodes, curves = self._animation_counts()
            definitions.extend(
                [
                    (b"AnimationStack", clips),
                    (b"AnimationLayer", clips),
                    (b"AnimationCurveNode", nodes),
                    (b"AnimationCurve", curves),
                ]
            )

        self._leaf(b"Count", [sum(count for _, count in definitions)])
        for name, count in definitions:
            with self._node(b"ObjectType", [name]):
                self._leaf(b"Count", [count])

                if name == b"Model":
                    with self._node(b"PropertyTemplate", [b"FbxNode"]):
                        self._props70([(b"Visibility", b"Visibility", b"", b"A", 1.0)])

    def _write_armature(self):
        armature_id = self._next_id()
        self._ctx["ROOT_ID"] = armature_id

        with self._node(b"Model", [armature_id, b"Armature\x00\x01Model", b"Null"]):
            self._props70([(b"InheritType", b"enum", b"", b"", 1)])

    def _write_bones(self):
        for bone in self.data.scene.skeleton.bones:
            fbx_id = self._next_id()
            self._ctx["BONES"][bone.id] = fbx_id

            name = bone.name.encode() + b"\x00\x01Model"
            with self._node(b"Model", [fbx_id, name, b"LimbNode"]):
                self._props70(
                    [
                        (b"Lcl Translation", b"Lcl Translation", b"", b"A", *bone.position.tolist()),
                        (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", *bone.rotation.tolist()),
                        (b"InheritType", b"enum", b"", b"", 1),
                    ]
                )

    def _write_bind_pose(self):
        pose_id = self._next_id()
        bones = self.data.scene.skeleton.bones

        with self._node(b"Pose", [pose_id, b"Pose\x00\x01Pose", b"BindPose"]):
            self._leaf(b"Type", [b"BindPose"])
            self._leaf(b"Version", [100])
            self._leaf(b"NbPoseNodes", [len(bones) + len(self.data.scene.meshes) + 1])

            with self._node(b"PoseNode"):
                self._leaf(b"Node", [self._ctx["ROOT_ID"]])
                self._leaf(b"Matrix", [np.eye(4, dtype=np.float64).flatten()])

            for mesh in self.data.scene.meshes:
                with self._node(b"PoseNode"):
                    self._leaf(b"Node", [self._ctx["MESHES"][mesh.name]["mesh"]])
                    self._leaf(b"Matrix", [np.eye(4, dtype=np.float64).flatten()])

            for bone, bind_matrix in zip(bones, self._ctx["BIND_POSE"]):
                with self._node(b"PoseNode"):
                    self._leaf(b"Node", [self._ctx["BONES"][bone.id]])
                    self._leaf(b"Matrix", [self.io.matrix(bind_matrix)])

    def _write_skinning(self, mesh: S.ModelMesh):
        skinning: Skinning = self._ctx["SKINNING"][mesh.name]
        if not skinning:
            return

        skin_id = self._next_id()
        ids = self._ctx["MESHES"][mesh.name]
        ids["skin"] = skin_id

        name = mesh.name.encode() + b"\x00\x01Deformer"
        with self._node(b"Deformer", [skin_id, name, b"Skin"]):
            self._leaf(b"Version", [101])
            self._leaf(b"Link_DeformAcuracy", [50.0])

        for bone_id, (indices, weights) in skinning.items():
            cluster_id = self._next_id()
            ids[f"cluster_{bone_id}"] = cluster_id
            bone = self.data.scene.skeleton.bones[bone_id]
            name = bone.name.encode() + b"\x00\x01SubDeformer"

            with self._node(b"Deformer", [cluster_id, name, b"Cluster"]):
                self._leaf(b"Version", [100])
                self._leaf(b"UserData", [b"", b""])
                self._leaf(b"Indexes", [indices])
                self._leaf(b"Weights", [weights])
                transform = np.linalg.inv(self._ctx["BIND_POSE"][bone_id])
                self._leaf(b"Transform", [self.io.matrix(transform)])
                self._leaf(b"TransformLink", [self.io.matrix(self._ctx["BIND_POSE"][bone_id])])
                self._leaf(b"TransformAssociateModel", [np.eye(4, dtype=np.float64).flatten()])

    def _write_bone_connections(self, root_id: np.int64):
        for bone in self.data.scene.skeleton.bones:
            child_id = self._ctx["BONES"][bone.id]
            parent_id = root_id if bone.is_root else self._ctx["BONES"][bone.parent_id]
            self._leaf(b"C", [b"OO", child_id, parent_id])

    def _write_cluster_connections(
        self,
        mesh: S.ModelMesh,
        ids: dict[str, np.int64],
    ):
        for bone_id in self._ctx["SKINNING"][mesh.name]:
            self._leaf(b"C", [b"OO", ids[f"cluster_{bone_id}"], ids["skin"]])
            self._leaf(b"C", [b"OO", self._ctx["BONES"][bone_id], ids[f"cluster_{bone_id}"]])

    def _write_animations(self):
        for clip, rotations in zip(self.data.scene.animation.clips, self._ctx["ROTATIONS"]):
            self._write_animation(clip, rotations)

    def _write_animation(
        self,
        clip: S.AnimationClip,
        rotations: np.ndarray,
    ):
        stack = self._next_id()
        layer = self._next_id()
        times = np.rint(clip.times * FBX.TICKS_PER_SECOND).astype(np.int64)
        end = times[-1] if times.size else np.int64(0)
        name = clip.name.encode()
        attributes = np.full(len(times), FBX.KEY_ATTRIBUTES, dtype=np.int32)
        references = np.ones(len(times), dtype=np.int32)
        curve_data = self.io.curve_data(times, attributes, references)

        with self._node(b"AnimationStack", [stack, name + b"\x00\x01AnimStack", b""]):
            self._props70(
                [
                    (b"LocalStart", b"KTime", b"Time", b"", np.int64(0)),
                    (b"LocalStop", b"KTime", b"Time", b"", end),
                    (b"ReferenceStart", b"KTime", b"Time", b"", np.int64(0)),
                    (b"ReferenceStop", b"KTime", b"Time", b"", end),
                ]
            )

        with self._node(b"AnimationLayer", [layer, name + b"\x00\x01AnimLayer", b""]):
            self._leaf(b"Version", [100])

        animation = AnimationNodes(stack, layer, [], [])
        for bone in self.data.scene.skeleton.bones:
            animation.translations.append(
                self._write_curve_node(
                    b"Lcl Translation",
                    times,
                    clip.translations[:, bone.id],
                    bone.position,
                    curve_data,
                )
            )
            animation.rotations.append(
                self._write_curve_node(
                    b"Lcl Rotation",
                    times,
                    rotations[:, bone.id],
                    bone.rotation,
                    curve_data,
                )
            )

        self._ctx["ANIMATIONS"].append(animation)

    def _write_curve_node(
        self,
        property: bytes,
        times: np.ndarray,
        values: np.ndarray,
        default: np.ndarray,
        curve_data: tuple[bytes, bytes, bytes],
    ) -> CurveNode | None:
        axes = np.any(values != default, axis=0)
        if not axes.any():
            return None

        node = self._next_id()
        self._leaf(b"AnimationCurveNode", [node, property + b"\x00\x01AnimCurveNode", b""])

        curves = tuple(
            (axis, self._write_curve(values[:, index], curve_data))
            for index, axis in enumerate(FBX.AXES)
            if axes[index]
        )
        return node, curves

    def _write_curve(
        self,
        values: np.ndarray,
        curve_data: tuple[bytes, bytes, bytes],
    ) -> np.int64:
        curve = self._next_id()
        self.io.animation_curve(
            curve,
            curve_data[0],
            values.astype(np.float32, copy=False),
            curve_data[1],
            curve_data[2],
            FBX.KEY_VERSION,
        )

        return curve

    def _write_animation_connections(self):
        for clip, animation in zip(self.data.scene.animation.clips, self._ctx["ANIMATIONS"]):
            self._leaf(b"C", [b"OO", animation.layer, animation.stack])

            for bone, translation, rotation in zip(
                self.data.scene.skeleton.bones,
                animation.translations,
                animation.rotations,
            ):
                if translation is not None:
                    self._write_curve_connections(
                        translation, animation.layer, self._ctx["BONES"][bone.id], b"Lcl Translation"
                    )
                if rotation is not None:
                    self._write_curve_connections(
                        rotation, animation.layer, self._ctx["BONES"][bone.id], b"Lcl Rotation"
                    )

    def _write_curve_connections(
        self,
        animation: CurveNode,
        layer: np.int64,
        bone: np.int64,
        property: bytes,
    ):
        node, curves = animation
        self._leaf(b"C", [b"OO", node, layer])
        self._leaf(b"C", [b"OP", node, bone, property])
        for axis, curve in curves:
            self._leaf(b"C", [b"OP", curve, node, axis])

    def _animation_counts(self) -> tuple[int, int]:
        nodes, curves = 0, 0

        for clip, rotations in zip(self.data.scene.animation.clips, self._ctx["ROTATIONS"]):
            for bone in self.data.scene.skeleton.bones:
                for values, default in (
                    (clip.translations[:, bone.id], bone.position),
                    (rotations[:, bone.id], bone.rotation),
                ):
                    axes = np.any(values != default, axis=0)
                    nodes += bool(axes.any())
                    curves += int(axes.sum())

        return nodes, curves

    def _mesh_skinning(
        self,
        mesh: S.ModelMesh,
    ) -> Skinning:
        active = mesh.links_weights > 0.0
        bone_ids = np.unique(mesh.links_ids[active])
        skinning: Skinning = {}

        for bone_id in bone_ids:
            rows, columns = np.where((mesh.links_ids == bone_id) & active)
            indices, inverse = np.unique(rows, return_inverse=True)
            weights = np.zeros(len(indices), dtype=np.float64)
            np.add.at(weights, inverse, mesh.links_weights[rows, columns])
            skinning[int(bone_id)] = indices.astype(np.int32), weights

        return skinning

    def _write_mesh(self, mesh: S.ModelMesh):
        fbx_id = self._next_id()
        self._ctx["MESHES"][mesh.name]["mesh"] = fbx_id

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
            self._leaf(b"Vertices", [mesh.vertices.astype(np.float32, copy=False).flatten()])
            self._leaf(b"PolygonVertexIndex", [self.io.polygon_indices(mesh.polygons)])
            self._leaf(b"Edges", [])

            with self._node(b"LayerElementMaterial", [0]):
                self._leaf(b"Version", [101])
                self._leaf(b"Name", [b""])
                self._leaf(b"MappingInformationType", [b"AllSame"])
                self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                self._leaf(b"Materials", [np.array([0], dtype=np.int32)])

            if self.includes(Feature.UV) and mesh.uv1.size:
                with self._node(b"LayerElementUV", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b"UVMap"])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"UV", [mesh.uv1.astype(np.float32, copy=False).flatten()])
                    self._leaf(b"UVIndex", [indexes])

            if self.includes(Feature.UV2) and mesh.uv2.size:
                with self._node(b"LayerElementUV", [1]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b"UVMap_2"])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"UV", [mesh.uv2.astype(np.float32, copy=False).flatten()])
                    self._leaf(b"UVIndex", [indexes])

            if self.includes(Feature.NORMALS) and mesh.normals.size:
                with self._node(b"LayerElementNormal", [0]):
                    self._leaf(b"Version", [101])
                    self._leaf(b"Name", [b""])
                    self._leaf(b"MappingInformationType", [b"ByPolygonVertex"])
                    self._leaf(b"ReferenceInformationType", [b"IndexToDirect"])
                    self._leaf(b"Normals", [mesh.normals.astype(np.float32, copy=False).flatten()])
                    self._leaf(b"NormalsIndex", [indexes])

            with self._node(b"Layer", [0]):
                self._leaf(b"Version", [100])

                with self._node(b"LayerElement", []):
                    self._leaf(b"Type", [b"Material"])
                    self._leaf(b"TypedIndex", [0])

                if self.includes(Feature.UV) and mesh.uv1.size:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"UV"])
                        self._leaf(b"TypedIndex", [0])

                if self.includes(Feature.UV2) and mesh.uv2.size:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"UV"])
                        self._leaf(b"TypedIndex", [1])

                if self.includes(Feature.NORMALS) and mesh.normals.size:
                    with self._node(b"LayerElement", []):
                        self._leaf(b"Type", [b"Normal"])
                        self._leaf(b"TypedIndex", [0])

        self._ctx["MESHES"][mesh.name]["geometry"] = geom_id

        mat_id = self._next_id()
        material_name = mesh.material.encode() + b"\x00\x01" + b"Material"
        with self._node(b"Material", [mat_id, material_name, b""]):
            self._leaf(b"Version", [102])
            self._props70(DEFAULT.MATERIAL)

        self._ctx["MESHES"][mesh.name]["material"] = mat_id

    @contextmanager
    def _node(self, name: bytes, properties: list | None = None, root: bool = False):
        self._start_node(name, properties, root)

        try:
            yield
        finally:
            self._end_node()

    def _leaf(self, name: bytes, properties: list | None = None, root: bool = False):
        if self._ctx["NODES"]:
            self._ctx["NODES"][-1]["children"] = True

        self.io.leaf(name, properties or [], root)

    def _props70(self, props: Props):
        with self._node(b"Properties70"):
            for prop in props:
                with self._node(b"P", list(prop)):
                    pass

    def _start_node(self, name: bytes, properties: list | None = None, root: bool = False):
        if self._ctx["NODES"]:
            self._ctx["NODES"][-1]["children"] = True

        properties = properties or []
        node_start = self.io.tell()

        self.io.header(0, 0, 0, name)

        props_start = self.io.tell()
        for prop in properties:
            self.io.property(prop)

        prop_len = self.io.tell() - props_start

        self._ctx["NODES"].append(
            dict(
                start=node_start,
                prop_count=len(properties),
                prop_len=prop_len,
                root=root,
                children=False,
            )
        )

    def _end_node(self):
        node = self._ctx["NODES"].pop()

        if node["root"] or node["children"]:
            self.io.write(FBX.NULL_NODE)

        end_pos = self.io.tell()

        self.io.seek(node["start"])
        self.io.header(end_pos, node["prop_count"], node["prop_len"])
        self.io.seek(end_pos)

    def _next_id(self) -> np.int64:
        self._ctx["NEXT_ID"] += 1
        return np.int64(self._ctx["NEXT_ID"])
