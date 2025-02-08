import xml.etree.ElementTree as etree
from typing import Optional
from xml.etree.ElementTree import Element, SubElement

import numpy as np

from scfile.core import FileEncoder
from scfile.core.context import ModelContent, ModelOptions
from scfile.enums import FileFormat
from scfile.formats.mcsa.flags import Flag
from scfile.geometry.mesh import ModelMesh
from scfile.geometry.skeleton import SkeletonBone, create_transform_matrix


DECLARATION = b'<?xml version="1.0" encoding="utf-8"?>\n'

XMLNS = "http://www.collada.org/2008/03/COLLADASchema"
VERSION = "1.5.0"

UP_AXIS = "Y_UP"

DEFAULT_COLOR = "1 1 1 1"


class DaeEncoder(FileEncoder[ModelContent, ModelOptions]):
    format = FileFormat.DAE

    _options = ModelOptions

    @property
    def skeleton_presented(self) -> bool:
        return self.data.flags[Flag.SKELETON] and self.options.parse_skeleton

    def prepare(self):
        self.data.scene.invert_v_textures()
        self.data.scene.ensure_unique_names()
        self.data.scene.skeleton.convert_to_local()
        self.data.scene.skeleton.build_hierarchy()

    def serialize(self):
        self.create_root()
        self.add_declaration()
        self.add_asset()
        self.add_effects()
        self.add_materials()
        self.add_geometries()

        if self.skeleton_presented:
            self.add_controllers()

        self.add_scenes()
        self.render_xml()

    def add_declaration(self):
        self.write(DECLARATION)

    def create_root(self):
        self.ctx["ROOT"] = Element("COLLADA", xmlns=XMLNS, version=VERSION)

    def add_asset(self):
        asset = SubElement(self.ctx["ROOT"], "asset")
        SubElement(asset, "unit", name="meter", meter="1")
        SubElement(asset, "up_axis").text = UP_AXIS

    def add_effects(self):
        library = SubElement(self.ctx["ROOT"], "library_effects")

        for mesh in self.data.meshes:
            effect = SubElement(library, "effect", id=f"{mesh.material}-effect")
            profile = SubElement(effect, "profile_COMMON")
            technique = SubElement(profile, "technique", sid="common")
            phong = SubElement(technique, "phong")
            diffuse = SubElement(phong, "diffuse")
            color = SubElement(diffuse, "color")
            color.text = DEFAULT_COLOR

    def add_materials(self):
        library = SubElement(self.ctx["ROOT"], "library_materials")

        for mesh in self.data.meshes:
            material = SubElement(library, "material", id=f"{mesh.material}-material", name=mesh.material)
            SubElement(material, "instance_effect", url=f"#{mesh.material}-effect")

    def create_source(
        self,
        parent: Element,
        id: str,
        name: str,
        data: np.ndarray,
        tag: str = "float_array",
        count: Optional[int] = None,
    ) -> Element:
        count = count or len(data)
        source = SubElement(parent, "source", id=f"{id}-{name}")
        array = SubElement(source, tag, id=f"{id}-{name}-array", count=str(count))
        array.text = " ".join(map(str, data.flatten()))
        return source

    def add_source_common(
        self,
        source: Element,
        id: str,
        name: str,
        count: int,
        components: list[str],
        datatype: str,
        stride: Optional[int] = None,
    ):
        array_id = f"#{id}-{name}-array"
        stride = stride or len(components)

        common = SubElement(source, "technique_common")
        accessor = SubElement(common, "accessor", source=array_id, count=str(count), stride=str(stride))

        for component in components:
            accessor.append(Element("param", name=component, type=datatype))

    def add_mesh_sources(self, mesh: ModelMesh, node: Element):
        # XYZ Positions
        pos_data = np.array(mesh.get_positions())
        pos_source = self.create_source(node, mesh.name, "positions", pos_data)
        self.add_source_common(pos_source, mesh.name, "positions", len(pos_data), ["X", "Y", "Z"], "float")

        # UV Texture
        if self.data.flags[Flag.TEXTURE]:
            tex_data = np.array(mesh.get_textures())
            tex_source = self.create_source(node, mesh.name, "texture", tex_data)
            self.add_source_common(tex_source, mesh.name, "texture", len(tex_data), ["S", "T"], "float")

        # XYZ Normals
        if self.data.flags[Flag.NORMALS]:
            norm_data = np.array(mesh.get_normals())
            norm_source = self.create_source(node, mesh.name, "normals", norm_data)
            self.add_source_common(norm_source, mesh.name, "normals", len(norm_data), ["X", "Y", "Z"], "float")

    def add_triangles(self, mesh: ModelMesh, node: Element):
        vertices = SubElement(node, "vertices", id=f"{mesh.name}-vertices")
        SubElement(vertices, "input", semantic="POSITION", source=f"#{mesh.name}-positions")

        triangles = SubElement(node, "triangles", count=str(mesh.count.polygons), material=f"{mesh.material}-material")

        # Inputs
        SubElement(triangles, "input", semantic="VERTEX", source=f"#{mesh.name}-vertices", offset="0")

        if self.data.flags[Flag.TEXTURE]:
            SubElement(triangles, "input", semantic="TEXCOORD", source=f"#{mesh.name}-texture", offset="0")

        if self.data.flags[Flag.NORMALS]:
            SubElement(triangles, "input", semantic="NORMAL", source=f"#{mesh.name}-normals", offset="0")

        # ABC Polygons
        indices = np.array(mesh.get_polygons())
        p = SubElement(triangles, "p")
        p.text = " ".join(map(str, indices))

    def add_geometries(self):
        library = SubElement(self.ctx["ROOT"], "library_geometries")

        for mesh in self.data.meshes:
            geometry = SubElement(library, "geometry", id=mesh.name, name=mesh.name)
            node = SubElement(geometry, "mesh")

            self.add_mesh_sources(mesh, node)
            self.add_triangles(mesh, node)

    def add_controllers(self):
        library = SubElement(self.ctx["ROOT"], "library_controllers")

        for mesh in self.data.meshes:
            controller = SubElement(library, "controller", id=f"{mesh.name}-skin", name="Armature")
            skin = SubElement(controller, "skin", source=f"#{mesh.name}")
            self.add_controller_sources(mesh, skin)
            self.add_joints_and_weights(mesh, skin)

    def add_controller_sources(self, mesh: ModelMesh, skin: Element):
        # Add joint names
        joint_data = np.array(self.data.skeleton.get_bones_names())
        joint_source = self.create_source(skin, mesh.name, "joints", joint_data, "Name_array")
        self.add_source_common(joint_source, mesh.name, "joints", len(joint_data), ["JOINT"], "name")

        # Add bind poses
        bind_data = self.data.skeleton.inverse_bind_matrices(transpose=False)
        bind_source = self.create_source(skin, mesh.name, "bindposes", bind_data, count=len(bind_data) * 16)
        self.add_source_common(bind_source, mesh.name, "bindposes", len(bind_data), ["TRANSFORM"], "float4x4", 16)

        # Add weights
        weight_data = np.array(mesh.get_bone_weights(max_links=mesh.count.max_links))
        weight_source = self.create_source(skin, mesh.name, "weights", weight_data)
        self.add_source_common(weight_source, mesh.name, "weights", len(weight_data), ["WEIGHT"], "float")

    def add_joints_and_weights(self, mesh: ModelMesh, skin: Element):
        # Add joints
        joints = SubElement(skin, "joints")
        SubElement(joints, "input", semantic="JOINT", source=f"#{mesh.name}-joints")
        SubElement(joints, "input", semantic="INV_BIND_MATRIX", source=f"#{mesh.name}-bindposes")

        # Add vertex weights
        weights = SubElement(skin, "vertex_weights", count=str(mesh.count.vertices))
        SubElement(weights, "input", semantic="JOINT", source=f"#{mesh.name}-joints", offset="0")
        SubElement(weights, "input", semantic="WEIGHT", source=f"#{mesh.name}-weights", offset="1")

        # Add indices
        SubElement(weights, "vcount").text = " ".join([str(mesh.count.max_links)] * mesh.count.vertices)
        SubElement(weights, "v").text = " ".join(mesh.get_bone_indices(mesh.count.max_links))

    def add_scenes(self):
        library = SubElement(self.ctx["ROOT"], "library_visual_scenes")
        visual_scene = SubElement(library, "visual_scene", id="scene", name="Scene")

        if self.skeleton_presented:
            visual_scene = self.add_armature(visual_scene)

        self.add_mesh_instances(visual_scene)

        scene = SubElement(self.ctx["ROOT"], "scene")
        SubElement(scene, "instance_visual_scene", url="#scene")

    def add_armature(self, scene: Element) -> Element:
        node = SubElement(scene, "node", id="armature", name="Armature", type="NODE")
        # SubElement(node, "matrix", sid="transform").text = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

        for root in self.data.skeleton.roots:
            self.add_bone(node, root)

        return node

    def add_bone(self, parent: Element, bone: "SkeletonBone"):
        joint = SubElement(parent, "node", id=f"armature-{bone.name}", sid=bone.name, name=bone.name, type="JOINT")

        matrix = create_transform_matrix(bone)
        SubElement(joint, "matrix", sid="transform").text = " ".join(map(str, matrix.flatten()))

        for child in bone.children:
            self.add_bone(joint, child)

    def add_mesh_instances(self, parent: Element):
        for mesh in self.data.meshes:
            node = SubElement(parent, "node", id=mesh.name, name=mesh.name, type="NODE")

            if self.skeleton_presented:
                bone = self.data.skeleton.roots[0]
                instance = SubElement(node, "instance_controller", url=f"#{mesh.name}-skin")
                SubElement(instance, "skeleton").text = f"#armature-{bone.name}"
            else:
                instance = SubElement(node, "instance_geometry", url=f"#{mesh.name}", name=mesh.name)

            self.add_bind_material(mesh, instance)

    def add_bind_material(self, mesh: ModelMesh, instance: Element):
        bind = SubElement(instance, "bind_material")
        technique_common = SubElement(bind, "technique_common")
        SubElement(
            technique_common,
            "instance_material",
            symbol=f"{mesh.material}-material",
            target=f"#{mesh.material}-material",
        )

    def render_xml(self):
        etree.indent(self.ctx["ROOT"])
        self.write(etree.tostring(self.ctx["ROOT"]))
