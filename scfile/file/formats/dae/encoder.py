import xml.etree.ElementTree as etree
from typing import Any

import numpy as np
from numpy.typing import NDArray

from scfile.file.base import FileEncoder
from scfile.file.data import ModelData
from scfile.utils.model.datatypes import Vector
from scfile.utils.model.skeleton import Bone


DEFAULT_MATRIX = "1 0 0 0  0 1 0 0  0 0 1 0 0 0 0 1"


class DaeEncoder(FileEncoder[ModelData]):
    def serialize(self):
        self.model = self.data.model
        self.flags = self.data.model.flags
        self.skeleton = self.data.model.skeleton

        self.model.ensure_unique_names()
        self.skeleton.convert_to_local()
        self.skeleton.build_hierarchy()

        self._create_root()
        self._add_asset()
        self._add_geometries()
        # self._add_controllers()
        self._add_scenes()
        self._render_xml()

    def _create_root(self):
        xmlns = "http://www.collada.org/2008/03/COLLADASchema"
        self.root = etree.Element("COLLADA", xmlns=xmlns, version="1.5.0")

    def _add_asset(self):
        asset = etree.SubElement(self.root, "asset")
        etree.SubElement(asset, "unit", name="meter", meter="1")
        etree.SubElement(asset, "up_axis").text = "Y_UP"

    def _add_geometries(self):
        library = etree.SubElement(self.root, "library_geometries")

        for mesh in self.model.meshes:
            geom = etree.SubElement(library, "geometry", id=f"{mesh.name}-mesh", name=mesh.name)
            self.node = etree.SubElement(geom, "mesh")

            self.mesh = mesh

            self._add_positions()
            self._add_normals()
            self._add_texture()
            self._add_vertices()
            self._add_triangles()

    def _add_positions(self):
        data = np.array([(v.position.x, v.position.y, v.position.z) for v in self.mesh.vertices])
        self._add_source("positions", data, ["X", "Y", "Z"])

    def _add_normals(self):
        data = np.array([(v.normals.x, v.normals.y, v.normals.z) for v in self.mesh.vertices])
        self._add_source("normals", data, ["X", "Y", "Z"])

    def _add_texture(self):
        data = np.array([(v.texture.u, -v.texture.v) for v in self.mesh.vertices])
        self._add_source("texture", data, ["S", "T"])

    def _add_source(self, name: str, data: NDArray[Any], components: list[str]):
        self.source = etree.SubElement(self.node, "source", id=f"{self.mesh.name}-{name}")

        array = etree.SubElement(
            self.source,
            "float_array",
            id=f"{self.mesh.name}-{name}-array",
            count=str(self.mesh.count.vertices),
        )

        array.text = " ".join(map(str, data.flatten()))

        self._add_source_common(name, components)

    def _add_source_common(self, name: str, components: list[str]):
        common = etree.SubElement(
            self.source,
            "technique_common",
        )
        accessor = etree.SubElement(
            common,
            "accessor",
            source=f"#{self.mesh.name}-{name}-array",
            count=str(self.mesh.count.vertices),
            stride=str(len(components)),
        )

        for name in components:
            accessor.append(etree.Element("param", name=name, type="float"))

    def _add_vertices(self):
        vertices = etree.SubElement(self.node, "vertices", id=f"{self.mesh.name}-vertices")
        etree.SubElement(
            vertices, "input", semantic="POSITION", source=f"#{self.mesh.name}-positions"
        )

    def _add_triangles(self):
        self.triangles = etree.SubElement(
            self.node, "triangles", count=str(self.mesh.count.polygons)
        )
        self._add_inputs()
        self._add_polygons()

    def _add_inputs(self):
        self._add_input("VERTEX", "vertices")

        if self.flags.normals:
            self._add_input("NORMAL", "normals")

        if self.flags.texture:
            self._add_input("TEXCOORD", "texture")

    def _add_input(self, semantic: str, name: str):
        etree.SubElement(
            self.triangles,
            "input",
            semantic=semantic,
            source=f"#{self.mesh.name}-{name}",
            offset="0",
        )

    def _add_polygons(self):
        indices = np.array([vertex_id for polygon in self.mesh.polygons for vertex_id in polygon])

        p = etree.SubElement(self.triangles, "p")
        p.text = " ".join(map(str, indices))

    def _add_controllers(self):
        library = etree.SubElement(self.root, "library_controllers")
        ctrl = etree.SubElement(library, "controller", id="skeleton-controller")

        self.skin = etree.SubElement(ctrl, "skin")
        etree.SubElement(self.skin, "bind_shape_matrix").text = DEFAULT_MATRIX

        self._add_joints_source()
        self._add_poses_source()

        joints = etree.SubElement(self.skin, "joints")
        etree.SubElement(joints, "input", semantic="JOINT", source="#skeleton-joints")
        etree.SubElement(joints, "input", semantic="INV_BIND_MATRIX", source="#skeleton-bindposes")

        weights = etree.SubElement(
            self.skin, "vertex_weights", count=str(self.model.total_vertices)
        )
        etree.SubElement(weights, "input", semantic="JOINT", source="#skeleton-joints")
        etree.SubElement(weights, "input", semantic="WEIGHT", source="#skeleton-bindposes")

    def _add_joints_source(self):
        count = str(len(self.skeleton.bones))

        joints_source = etree.SubElement(self.skin, "source", id="skeleton-joints")
        array = etree.SubElement(
            joints_source,
            "Name_array",
            id="skeleton-joints-array",
            count=count,
        )
        array.text = " ".join([bone.name for bone in self.skeleton.bones])

        common = etree.SubElement(
            joints_source,
            "technique_common",
        )
        accessor = etree.SubElement(
            common,
            "accessor",
            source="#skeleton-joints-array",
            count=count,
            stride="1",
        )

        etree.SubElement(accessor, "param", name="JOINT", type="Name")

    def _add_poses_source(self):
        count = str(len(self.skeleton.bones) * 16)

        poses_source = etree.SubElement(self.skin, "source", id="skeleton-bindposes")
        array = etree.SubElement(
            poses_source,
            "float_array",
            id="skeleton-bindposes-array",
            count=count,
        )
        array.text = " ".join([DEFAULT_MATRIX for _ in self.skeleton.bones])

        common = etree.SubElement(
            poses_source,
            "technique_common",
        )
        accessor = etree.SubElement(
            common,
            "accessor",
            source="#skeleton-bindposes-array",
            count=count,
            stride="16",
        )

        etree.SubElement(accessor, "param", name="TRANSFORM", type="float4x4")

    def _add_scenes(self):
        library = etree.SubElement(self.root, "library_visual_scenes")
        visual_scene = etree.SubElement(library, "visual_scene", id="scene")

        for mesh in self.model.meshes:
            node = etree.SubElement(
                visual_scene, "node", id=f"{mesh.name}-node", name=mesh.name, type="NODE"
            )
            etree.SubElement(node, "instance_geometry", url=f"#{mesh.name}-mesh", name=mesh.name)

        if self.flags.skeleton:
            skeleton_node = etree.SubElement(
                visual_scene, "node", id="skeleton-node", name="skeleton", type="NODE"
            )

            def add_bone(bone: Bone, parent_node: etree.Element):
                node = etree.SubElement(
                    parent_node, "node", id=f"{bone.name}-bone", name=bone.name, type="JOINT"
                )
                etree.SubElement(node, "translate").text = " ".join(map(str, bone.position))

                for child in bone.children:
                    add_bone(child, node)

            root = self.skeleton.bones[0]
            for child in root.children:
                add_bone(child, skeleton_node)

        scene = etree.SubElement(self.root, "scene")
        etree.SubElement(scene, "instance_visual_scene", url="#scene")

    def _render_xml(self):
        etree.indent(self.root)
        self.buffer.write(etree.tostring(self.root))
