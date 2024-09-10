import xml.etree.ElementTree as etree

import numpy as np

from scfile.enums import FileSuffix
from scfile.file.base import FileEncoder
from scfile.file.data import ModelData
from scfile.utils.model.skeleton import Bone


class DaeEncoder(FileEncoder[ModelData]):
    @classmethod
    def suffix(cls):
        return FileSuffix.DAE

    def serialize(self):
        # Aliases
        self.model = self.data.model
        self.flags = self.data.model.flags
        self.skeleton = self.data.model.skeleton

        # Prepare model
        self.model.ensure_unique_names()
        self.skeleton.convert_to_local()
        self.skeleton.build_hierarchy()

        # Build file
        self._create_root()
        self._add_asset()
        self._add_geometries()
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

    def _add_source(self, name: str, data: np.ndarray, components: list[str]):
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
        etree.SubElement(vertices, "input", semantic="POSITION", source=f"#{self.mesh.name}-positions")

    def _add_triangles(self):
        self.triangles = etree.SubElement(self.node, "triangles", count=str(self.mesh.count.polygons))
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

        name = "body"
        controller = etree.SubElement(library, "controller", id=f"{name}-controller")
        etree.SubElement(controller, "skin", source=f"#{name}-mesh")

        vertex_weights = etree.SubElement(controller, "vertex_weights")
        etree.SubElement(vertex_weights, "input", semantic="JOINT", source=f"#{name}-skin-joints")
        etree.SubElement(vertex_weights, "input", semantic="WEIGHT", source=f"#{name}-skin-weights")

    def _add_meshes(self):
        for mesh in self.model.meshes:
            node = etree.SubElement(self.scene, "node", id=f"{mesh.name}-node", name=mesh.name, type="NODE")
            etree.SubElement(node, "instance_geometry", url=f"#{mesh.name}-mesh", name=mesh.name)

    def _add_bone(self, element: etree.Element, bone: Bone):
        node = etree.SubElement(element, "node", id=f"{bone.id}-bone", name=bone.name, type="JOINT")

        etree.SubElement(node, "translate").text = " ".join(map(str, bone.position))
        etree.SubElement(node, "rotate").text = " ".join(map(str, bone.rotation))

        for child in bone.children:
            self._add_bone(node, child)

    def _add_skeleton(self):
        for bone in self.skeleton.roots:
            self._add_bone(self.scene, bone)

    def _add_scenes(self):
        library = etree.SubElement(self.root, "library_visual_scenes")
        self.scene = etree.SubElement(library, "visual_scene", id="scene")

        self._add_meshes()
        self._add_controllers()

        if self.flags.skeleton:
            self._add_skeleton()

        scene = etree.SubElement(self.root, "scene")
        etree.SubElement(scene, "instance_visual_scene", url="#scene")

    def _render_xml(self):
        etree.indent(self.root)
        self.buffer.write(etree.tostring(self.root))
