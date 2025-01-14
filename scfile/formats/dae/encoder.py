import xml.etree.ElementTree as etree
from typing import Optional

import numpy as np

from scfile.core import FileEncoder, ModelContext
from scfile.core.options import ModelOptions
from scfile.enums import FileFormat
from scfile.formats.mcsa.flags import Flag
from scfile.utils.model.mesh import ModelMesh
from scfile.utils.model.skeleton import SkeletonBone, create_transform_matrix


DECLARATION = b'<?xml version="1.0" encoding="utf-8"?>\n'

XMLNS = "http://www.collada.org/2008/03/COLLADASchema"
VERSION = "1.5.0"

UP_AXIS = "Y_UP"


class DaeEncoder(FileEncoder[ModelContext, ModelOptions]):
    format = FileFormat.DAE

    _options = ModelOptions

    @property
    def skeleton_present(self) -> bool:
        return self.ctx.flags[Flag.SKELETON] and self.options.parse_skeleton

    def prepare(self):
        self.ctx.scene.ensure_unique_names()
        self.ctx.scene.skeleton.convert_to_local()
        self.ctx.scene.skeleton.build_hierarchy()

    def serialize(self):
        root = self.create_root()
        self.add_declaration()
        self.add_asset(root)
        self.add_geometries(root)

        if self.skeleton_present:
            self.add_controllers(root)

        self.add_scenes(root)
        self.render_xml(root)

    def add_declaration(self):
        self.buffer.write(DECLARATION)

    def create_root(self) -> etree.Element:
        return etree.Element("COLLADA", xmlns=XMLNS, version=VERSION)

    def add_asset(self, root: etree.Element):
        asset = etree.SubElement(root, "asset")
        etree.SubElement(asset, "unit", name="meter", meter="1")
        etree.SubElement(asset, "up_axis").text = UP_AXIS

    def create_source(
        self,
        parent: etree.Element,
        mesh_name: str,
        name: str,
        data: np.ndarray,
        tag: str = "float_array",
        count: Optional[int] = None,
    ) -> etree.Element:
        count = count or len(data)
        source = etree.SubElement(parent, "source", id=f"{mesh_name}-{name}")
        array = etree.SubElement(source, tag, id=f"{mesh_name}-{name}-array", count=str(count))
        array.text = " ".join(map(str, data.flatten()))
        return source

    def add_source_common(
        self,
        source: etree.Element,
        mesh_name: str,
        name: str,
        count: int,
        components: list[str],
        type_: str,
        stride: Optional[int] = None,
    ):
        array_id = f"#{mesh_name}-{name}-array"
        stride = stride or len(components)

        common = etree.SubElement(source, "technique_common")
        accessor = etree.SubElement(common, "accessor", source=array_id, count=str(count), stride=str(stride))

        for component in components:
            accessor.append(etree.Element("param", name=component, type=type_))

    def add_mesh_sources(self, mesh_node: etree.Element, mesh: ModelMesh):
        # Positions XYZ
        pos_data = np.array([list(v.position) for v in mesh.vertices])
        pos_source = self.create_source(mesh_node, mesh.name, "positions", pos_data)
        self.add_source_common(pos_source, mesh.name, "positions", len(pos_data), ["X", "Y", "Z"], "float")

        # Normals XUZ
        if self.ctx.flags[Flag.NORMALS]:
            norm_data = np.array([list(v.normals) for v in mesh.vertices])
            norm_source = self.create_source(mesh_node, mesh.name, "normals", norm_data)
            self.add_source_common(norm_source, mesh.name, "normals", len(norm_data), ["X", "Y", "Z"], "float")

        # Texture UV
        if self.ctx.flags[Flag.TEXTURE]:
            tex_data = np.array([(v.texture.u, -v.texture.v) for v in mesh.vertices])
            tex_source = self.create_source(mesh_node, mesh.name, "texture", tex_data)
            self.add_source_common(tex_source, mesh.name, "texture", len(tex_data), ["S", "T"], "float")

    def add_triangles(self, mesh_node: etree.Element, mesh: ModelMesh):
        vertices = etree.SubElement(mesh_node, "vertices", id=f"{mesh.name}-vertices")
        etree.SubElement(vertices, "input", semantic="POSITION", source=f"#{mesh.name}-positions")

        triangles = etree.SubElement(mesh_node, "triangles", count=str(mesh.count.polygons))

        # Inputs
        etree.SubElement(triangles, "input", semantic="VERTEX", source=f"#{mesh.name}-vertices", offset="0")

        if self.ctx.flags[Flag.TEXTURE]:
            etree.SubElement(triangles, "input", semantic="TEXCOORD", source=f"#{mesh.name}-texture", offset="0")

        if self.ctx.flags[Flag.NORMALS]:
            etree.SubElement(triangles, "input", semantic="NORMAL", source=f"#{mesh.name}-normals", offset="0")

        # Polygons ABC
        indices = np.array([vertex_id for polygon in mesh.polygons for vertex_id in polygon])
        p = etree.SubElement(triangles, "p")
        p.text = " ".join(map(str, indices))

    def add_geometries(self, root: etree.Element):
        library = etree.SubElement(root, "library_geometries")

        for mesh in self.ctx.meshes:
            geom = etree.SubElement(library, "geometry", id=mesh.name, name=mesh.name)
            mesh_node = etree.SubElement(geom, "mesh")

            self.add_mesh_sources(mesh_node, mesh)
            self.add_triangles(mesh_node, mesh)

    def add_controllers(self, root: etree.Element):
        library = etree.SubElement(root, "library_controllers")

        for mesh in self.ctx.meshes:
            controller = etree.SubElement(library, "controller", id=f"{mesh.name}-skin", name="Armature")
            skin_node = etree.SubElement(controller, "skin", source=f"#{mesh.name}")
            etree.SubElement(skin_node, "bind_shape_matrix").text = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

            self.add_controller_sources(skin_node, mesh)
            self.add_joints_and_weights(skin_node, mesh)

    def add_controller_sources(self, skin_node: etree.Element, mesh: ModelMesh):
        # Add joint names
        joint_data = np.array([b.name for b in self.ctx.skeleton.bones])
        joint_source = self.create_source(skin_node, mesh.name, "joints", joint_data, "Name_array")
        self.add_source_common(joint_source, mesh.name, "joints", len(joint_data), ["JOINT"], "name")

        # Add bind poses
        bind_data = np.array(self.ctx.skeleton.calculate_inverse_bind_matrices())
        bind_source = self.create_source(skin_node, mesh.name, "bindposes", bind_data, count=len(bind_data) * 16)
        self.add_source_common(bind_source, mesh.name, "bindposes", len(bind_data), ["TRANSFORM"], "float4x4", 16)

        # Add weights
        weight_data = np.array([v.bone_weights[:1] for v in mesh.vertices])
        weight_source = self.create_source(skin_node, mesh.name, "weights", weight_data)
        self.add_source_common(weight_source, mesh.name, "weights", len(weight_data), ["WEIGHT"], "float")

    def add_joints_and_weights(self, skin_node: etree.Element, mesh: ModelMesh):
        # Add joints
        joints = etree.SubElement(skin_node, "joints")
        etree.SubElement(joints, "input", semantic="JOINT", source=f"#{mesh.name}-joints")
        etree.SubElement(joints, "input", semantic="INV_BIND_MATRIX", source=f"#{mesh.name}-bindposes")

        # Add vertex weights
        weights = etree.SubElement(skin_node, "vertex_weights", count=str(mesh.count.vertices))
        etree.SubElement(weights, "input", semantic="JOINT", source=f"#{mesh.name}-joints", offset="0")
        etree.SubElement(weights, "input", semantic="WEIGHT", source=f"#{mesh.name}-weights", offset="1")

        # TODO: figure out why tf zeros in ids and weights...
        etree.SubElement(weights, "vcount").text = " ".join(["1"] * mesh.count.vertices)
        etree.SubElement(weights, "v").text = " ".join(mesh.bone_indices)

    def add_scenes(self, root: etree.Element):
        library = etree.SubElement(root, "library_visual_scenes")
        scene = etree.SubElement(library, "visual_scene", id="scene", name="Scene")

        root_node = scene
        if self.skeleton_present:
            root_node = self.add_armature(scene)

        self.add_mesh_instances(root_node)

        scene_elem = etree.SubElement(root, "scene")
        etree.SubElement(scene_elem, "instance_visual_scene", url="#scene")

    def add_armature(self, scene: etree.Element) -> etree.Element:
        node = etree.SubElement(scene, "node", id="armature", name="Armature", type="NODE")
        etree.SubElement(node, "matrix", sid="transform").text = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

        for root in self.ctx.skeleton.roots:
            self.add_bone(node, root)

        return node

    def add_bone(self, parent: etree.Element, bone: "SkeletonBone"):
        joint = etree.SubElement(
            parent, "node", id=f"armature-{bone.name}", sid=bone.name, name=bone.name, type="JOINT"
        )

        matrix = create_transform_matrix(bone)
        etree.SubElement(joint, "matrix", sid="transform").text = " ".join(map(str, matrix.flatten()))

        for child in bone.children:
            self.add_bone(joint, child)

    def add_mesh_instances(self, parent: etree.Element):
        for mesh in self.ctx.meshes:
            node = etree.SubElement(parent, "node", id=mesh.name, name=mesh.name, type="NODE")

            if self.skeleton_present:
                bone = self.ctx.skeleton.roots[0]
                skin = etree.SubElement(node, "instance_controller", url=f"#{mesh.name}-skin")
                etree.SubElement(skin, "skeleton").text = f"#armature-{bone.name}"
            else:
                etree.SubElement(node, "instance_geometry", url=f"#{mesh.name}", name=mesh.name)

    def render_xml(self, root: etree.Element):
        etree.indent(root)
        self.buffer.write(etree.tostring(root))
