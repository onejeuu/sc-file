import xml.etree.ElementTree as etree

import numpy as np

from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag


class DaeSerializer(FileSerializer[ModelData]):
    @property
    def model(self):
        return self.data.model

    @property
    def flags(self):
        return self.data.flags

    def serialize(self):
        self.create_root()
        self.add_asset()
        self.add_geometries()
        self.add_scenes()
        self.render_xml()

    def create_root(self):
        xmlns = "http://www.collada.org/2008/03/COLLADASchema"
        self.root = etree.Element("COLLADA", xmlns=xmlns, version="1.5.0")

    def add_asset(self):
        asset = etree.SubElement(self.root, "asset")
        etree.SubElement(asset, "unit", name="meter", meter="1")
        etree.SubElement(asset, "up_axis").text = "Y_UP"

    def add_geometries(self):
        library = etree.SubElement(self.root, "library_geometries")

        for mesh in self.model.meshes:
            geom = etree.SubElement(library, "geometry", name=mesh.name, id=f"{mesh.name}-mesh")
            self.node = etree.SubElement(geom, "mesh")

            self.mesh = mesh

            self.add_vertices()
            self.add_positions()
            self.add_normals()
            self.add_texture()
            self.add_triangles()

    def add_positions(self):
        data = np.array([(v.position.x, v.position.y, v.position.z) for v in self.mesh.vertices])
        self.add_source("positions", data, ["X", "Y", "Z"])

    def add_normals(self):
        data = np.array([(v.normals.x, v.normals.y, v.normals.z) for v in self.mesh.vertices])
        self.add_source("normals", data, ["X", "Y", "Z"])

    def add_texture(self):
        data = np.array([(v.texture.u, -v.texture.v) for v in self.mesh.vertices])
        self.add_source("texture", data, ["S", "T"])

    def add_source(self, name: str, data: np.ndarray, components: list[str]):
        self.source = etree.SubElement(self.node, "source", id=f"{self.mesh.name}-{name}")

        array = etree.SubElement(
            self.source,
            "float_array",
            id=f"{self.mesh.name}-{name}-array",
            count=str(self.mesh.count.vertices),
        )

        array.text = " ".join(map(str, data.flatten()))

        self.add_source_common(name, components)

    def add_source_common(self, name: str, components: list[str]):
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

    def add_vertices(self):
        vertices = etree.SubElement(self.node, "vertices", id=f"{self.mesh.name}-vertices")
        etree.SubElement(vertices, "input", semantic="POSITION", source=f"#{self.mesh.name}-positions")

    def add_triangles(self):
        self.triangles = etree.SubElement(self.node, "triangles", count=str(self.mesh.count.polygons))
        self.add_inputs()
        self.add_polygons()

    def add_inputs(self):
        self.add_input("VERTEX", "vertices")

        if self.flags[Flag.TEXTURE]:
            self.add_input("TEXCOORD", "texture")

        if self.flags[Flag.NORMALS]:
            self.add_input("NORMAL", "normals")

    def add_input(self, semantic: str, name: str):
        etree.SubElement(
            self.triangles,
            "input",
            semantic=semantic,
            source=f"#{self.mesh.name}-{name}",
            offset="0",
        )

    def add_polygons(self):
        indices = np.array([vertex_id for polygon in self.mesh.polygons for vertex_id in polygon])

        p = etree.SubElement(self.triangles, "p")
        p.text = " ".join(map(str, indices))

    def add_controllers(self):
        library = etree.SubElement(self.root, "library_controllers")

        name = "body"
        controller = etree.SubElement(library, "controller", id=f"{name}-controller")
        etree.SubElement(controller, "skin", source=f"#{name}-mesh")

        vertex_weights = etree.SubElement(controller, "vertex_weights")
        etree.SubElement(vertex_weights, "input", semantic="JOINT", source=f"#{name}-skin-joints")
        etree.SubElement(vertex_weights, "input", semantic="WEIGHT", source=f"#{name}-skin-weights")

    def add_meshes(self):
        for mesh in self.model.meshes:
            node = etree.SubElement(self.scene, "node", name=mesh.name, id=f"{mesh.name}-node", type="NODE")
            etree.SubElement(node, "instance_geometry", name=mesh.name, url=f"#{mesh.name}-mesh")

    def add_scenes(self):
        library = etree.SubElement(self.root, "library_visual_scenes")
        self.scene = etree.SubElement(library, "visual_scene", name="Scene", id="scene")

        self.add_meshes()
        self.add_controllers()

        scene = etree.SubElement(self.root, "scene")
        etree.SubElement(scene, "instance_visual_scene", url="#scene")

    def render_xml(self):
        etree.indent(self.root)
        self.buffer.write(etree.tostring(self.root))
