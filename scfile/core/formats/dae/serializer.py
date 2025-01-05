import xml.etree.ElementTree as etree
from typing import Optional

import numpy as np

from scfile.consts import McsaModel
from scfile.core.base.serializer import FileSerializer
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.flags import Flag
from scfile.utils.model.skeleton import SkeletonBone, create_transform_matrix


UP_AXIS = "Y_UP"


class DaeSerializer(FileSerializer[ModelData]):
    @property
    def model(self):
        return self.data.model

    @property
    def flags(self):
        return self.data.flags

    def serialize(self):
        self.add_declaration()
        self.create_root()
        self.add_asset()
        self.add_geometries()
        self.add_controllers()
        self.add_scenes()
        self.render_xml()

    def add_declaration(self):
        self.buffer.write(b'<?xml version="1.0" encoding="utf-8"?>\n')

    def create_root(self):
        xmlns = "http://www.collada.org/2008/03/COLLADASchema"
        self.root = etree.Element("COLLADA", xmlns=xmlns, version="1.5.0")

    def add_asset(self):
        asset = etree.SubElement(self.root, "asset")
        etree.SubElement(asset, "unit", name="meter", meter="1")
        etree.SubElement(asset, "up_axis").text = UP_AXIS

    def add_geometries(self):
        library = etree.SubElement(self.root, "library_geometries")

        for mesh in self.model.meshes:
            geom = etree.SubElement(library, "geometry", id=mesh.id, name=mesh.name)
            self.node = etree.SubElement(geom, "mesh")

            self.mesh = mesh

            self.add_positions()
            self.add_normals()
            self.add_texture()
            self.add_vertices()
            self.add_triangles()

    def add_positions(self):
        name = "positions"
        data = np.array([(v.position.x, v.position.y, v.position.z) for v in self.mesh.vertices])
        source = self.add_source(name, data)
        self.add_source_common(source, name, len(data), ["X", "Y", "Z"], "float")

    def add_normals(self):
        name = "normals"
        data = np.array([(v.normals.x, v.normals.y, v.normals.z) for v in self.mesh.vertices])
        source = self.add_source(name, data)
        self.add_source_common(source, name, len(data), ["X", "Y", "Z"], "float")

    def add_texture(self):
        name = "texture"
        data = np.array([(v.texture.u, -v.texture.v) for v in self.mesh.vertices])
        source = self.add_source(name, data)
        self.add_source_common(source, name, len(data), ["S", "T"], "float")

    def add_source(self, name: str, data: np.ndarray, tag: str = "float_array", count: Optional[int] = None):
        count = count or len(data)
        source = etree.SubElement(self.node, "source", id=f"{self.mesh.id}-{name}")
        array = etree.SubElement(source, tag, id=f"{self.mesh.id}-{name}-array", count=str(count))
        array.text = " ".join(map(str, data.flatten()))
        return source

    def add_source_common(
        self,
        source: etree.Element,
        name: str,
        count: int,
        components: list[str],
        type: str,
        stride: Optional[int] = None,
    ):
        array_id = f"#{self.mesh.id}-{name}-array"
        stride = stride or len(components)

        common = etree.SubElement(source, "technique_common")
        accessor = etree.SubElement(common, "accessor", source=array_id, count=str(count), stride=str(stride))

        for name in components:
            accessor.append(etree.Element("param", name=name, type=type))

    def add_vertices(self):
        vertices = etree.SubElement(self.node, "vertices", id=f"{self.mesh.id}-vertices")
        etree.SubElement(vertices, "input", semantic="POSITION", source=f"#{self.mesh.id}-positions")

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
            source=f"#{self.mesh.id}-{name}",
            offset="0",
        )

    def add_polygons(self):
        indices = np.array([vertex_id for polygon in self.mesh.polygons for vertex_id in polygon])

        p = etree.SubElement(self.triangles, "p")
        p.text = " ".join(map(str, indices))

    def add_joints(self):
        name = "joints"
        data = np.array([b.name for b in self.model.skeleton.bones])
        source = self.add_source(name, data, "Name_array")
        self.add_source_common(source, name, len(data), ["JOINT"], "name")

    def add_bindposes(self):
        name = "bindposes"
        data = np.array(self.model.skeleton.calculate_bind_poses())
        source = self.add_source(name, data, count=len(data) * 16)
        self.add_source_common(source, name, len(data), ["TRANSFORM"], "float4x4", 16)

    def add_weights(self):
        name = "weights"
        links = self.mesh.count.max_links
        data = np.array([v.bone_weights[:links] for v in self.mesh.vertices])
        source = self.add_source(name, data)
        self.add_source_common(source, name, len(data), ["WEIGHT"], "float")

    def add_controllers(self):
        library = etree.SubElement(self.root, "library_controllers")

        controller = etree.SubElement(library, "controller", id=f"{self.mesh.id}-skin", name="Armature")
        self.node = skin = etree.SubElement(controller, "skin", source=f"#{self.mesh.id}")
        etree.SubElement(skin, "bind_shape_matrix").text = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

        self.add_joints()
        self.add_bindposes()
        self.add_weights()

        joints = etree.SubElement(skin, "joints")
        etree.SubElement(joints, "input", semantic="JOINT", source=f"#{self.mesh.id}-joints")
        etree.SubElement(joints, "input", semantic="INV_BIND_MATRIX", source=f"#{self.mesh.id}-bindposes")

        weights = etree.SubElement(skin, "vertex_weights", count=str(self.mesh.count.vertices))
        etree.SubElement(weights, "input", semantic="JOINT", source=f"#{self.mesh.id}-joints", offset="0")
        etree.SubElement(weights, "input", semantic="WEIGHT", source=f"#{self.mesh.id}-weights", offset="1")

        links = self.mesh.count.max_links
        v = []

        for index, vertex in enumerate(self.mesh.vertices):
            for bone_id in vertex.bone_ids[:links]:
                v.append(f"{bone_id} {index}")

        etree.SubElement(weights, "vcount").text = " ".join([str(links)] * self.mesh.count.vertices)
        etree.SubElement(weights, "v").text = " ".join(v)

    def add_bone(self, node: etree.Element, bone: SkeletonBone):
        joint = etree.SubElement(node, "node", id=f"armature-{bone.name}", sid=bone.name, name=bone.name, type="JOINT")

        matrix = create_transform_matrix(bone.position, bone.rotation)
        etree.SubElement(joint, "matrix", sid="transform").text = " ".join(map(str, matrix.flatten()))

        for child in bone.children:
            self.add_bone(joint, child)

    def add_armature(self):
        self.root_node = node = etree.SubElement(self.scene, "node", id="armature", name="Armature", type="NODE")
        etree.SubElement(node, "matrix", sid="transform").text = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

        for root in self.model.skeleton.roots:
            self.add_bone(node, root)

    def add_meshes(self):
        for mesh in self.model.meshes:
            node = etree.SubElement(self.root_node, "node", id=mesh.name, name=mesh.name, type="NODE")

            if not self.flags[Flag.SKELETON]:
                etree.SubElement(node, "instance_geometry", url=f"#{mesh.id}", name=mesh.name)

            else:
                bone = self.model.skeleton.roots[0]
                skin = etree.SubElement(node, "instance_controller", url=f"#{mesh.id}-skin")
                etree.SubElement(skin, "skeleton").text = f"#armature-{bone.name}"

    def add_scenes(self):
        library = etree.SubElement(self.root, "library_visual_scenes")
        self.root_node = self.scene = etree.SubElement(library, "visual_scene", id="scene", name="Scene")

        if self.flags[Flag.SKELETON]:
            self.add_armature()

        self.add_meshes()

        scene = etree.SubElement(self.root, "scene")
        etree.SubElement(scene, "instance_visual_scene", url="#scene")

    def render_xml(self):
        etree.indent(self.root)
        self.buffer.write(etree.tostring(self.root))
