import itertools
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import Element, SubElement

import numpy as np

from scfile.core import FileEncoder, ModelContent
from scfile.enums import FileFormat
from scfile.structures.flags import Flag
from scfile.structures.mesh import ModelMesh
from scfile.structures.skeleton import SkeletonBone, create_transform_matrix

from . import utils


VERSION = "1.5.0"

DECLARATION = b'<?xml version="1.0" encoding="utf-8"?>\n'
XMLNS = "http://www.collada.org/2008/03/COLLADASchema"

UP_AXIS = "Y_UP"

DEFAULT_COLOR = "1 1 1 1"


class DaeEncoder(FileEncoder[ModelContent]):
    format = FileFormat.DAE

    def prepare(self):
        self.data.scene.ensure_unique_names()

        if self.data.flags[Flag.UV]:
            self.data.scene.invert_v_textures()

        if self._skeleton_presented:
            self.data.scene.skeleton.convert_to_local()
            self.data.scene.skeleton.build_hierarchy()

    def serialize(self):
        self.ctx["ROOT"] = Element("COLLADA", xmlns=XMLNS, version=VERSION)
        self.write(DECLARATION)

        self._add_asset()
        self._add_effects()
        self._add_materials()
        self._add_geometries()

        if self._skeleton_presented:
            self._add_controllers()

        self._add_scenes()

        # Render XML
        etree.indent(self.ctx["ROOT"])
        self.write(etree.tostring(self.ctx["ROOT"]))

    def _add_asset(self):
        asset = SubElement(self.ctx["ROOT"], "asset")
        SubElement(asset, "unit", name="meter", meter="1")
        SubElement(asset, "up_axis").text = UP_AXIS

    def _add_effects(self):
        library = SubElement(self.ctx["ROOT"], "library_effects")

        for mesh in self.data.scene.meshes:
            effect = SubElement(library, "effect", id=f"{mesh.material}-effect")
            profile = SubElement(effect, "profile_COMMON")
            technique = SubElement(profile, "technique", sid="common")
            phong = SubElement(technique, "phong")
            diffuse = SubElement(phong, "diffuse")
            color = SubElement(diffuse, "color")
            color.text = DEFAULT_COLOR

    def _add_materials(self):
        library = SubElement(self.ctx["ROOT"], "library_materials")

        for mesh in self.data.scene.meshes:
            material = SubElement(library, "material", id=f"{mesh.material}-material", name=mesh.material)
            SubElement(material, "instance_effect", url=f"#{mesh.material}-effect")

    def _add_mesh_sources(self, mesh: ModelMesh, node: Element):
        # XYZ Positions
        pos_source = utils.create_source(node, mesh.name, "positions", mesh.positions)
        utils.add_accessor(pos_source, mesh.name, "positions", len(mesh.positions), ["X", "Y", "Z"], "float")

        # UV Texture
        if self.data.flags[Flag.UV]:
            tex_source = utils.create_source(node, mesh.name, "texture", mesh.textures)
            utils.add_accessor(tex_source, mesh.name, "texture", len(mesh.textures), ["S", "T"], "float")

        # XYZ Normals
        if self.data.flags[Flag.NORMALS]:
            norm_source = utils.create_source(node, mesh.name, "normals", mesh.normals)
            utils.add_accessor(norm_source, mesh.name, "normals", len(mesh.normals), ["X", "Y", "Z"], "float")

    def _add_triangles(self, mesh: ModelMesh, node: Element):
        vertices = SubElement(node, "vertices", id=f"{mesh.name}-vertices")
        SubElement(vertices, "input", semantic="POSITION", source=f"#{mesh.name}-positions")

        triangles = SubElement(node, "triangles", count=str(mesh.count.polygons), material=f"{mesh.material}-material")

        # Inputs
        SubElement(triangles, "input", semantic="VERTEX", source=f"#{mesh.name}-vertices", offset="0")

        if self.data.flags[Flag.UV]:
            SubElement(triangles, "input", semantic="TEXCOORD", source=f"#{mesh.name}-texture", offset="0")

        if self.data.flags[Flag.NORMALS]:
            SubElement(triangles, "input", semantic="NORMAL", source=f"#{mesh.name}-normals", offset="0")

        # ABC Polygons
        p = SubElement(triangles, "p")
        p.text = " ".join(map(str, mesh.polygons.flatten()))

    def _add_geometries(self):
        library = SubElement(self.ctx["ROOT"], "library_geometries")

        for mesh in self.data.scene.meshes:
            geometry = SubElement(library, "geometry", id=mesh.name, name=mesh.name)
            node = SubElement(geometry, "mesh")

            self._add_mesh_sources(mesh, node)
            self._add_triangles(mesh, node)

    def _add_controllers(self):
        library = SubElement(self.ctx["ROOT"], "library_controllers")

        for mesh in self.data.scene.meshes:
            controller = SubElement(library, "controller", id=f"{mesh.name}-skin", name="Armature")
            skin = SubElement(controller, "skin", source=f"#{mesh.name}")
            self._add_controller_sources(mesh, skin)
            self._add_joints_and_weights(mesh, skin)

    def _add_controller_sources(self, mesh: ModelMesh, skin: Element):
        # Add joint names
        joint_data = np.array([bone.name for bone in self.data.scene.skeleton.bones])
        joint_source = utils.create_source(skin, mesh.name, "joints", joint_data, "Name_array")
        utils.add_accessor(joint_source, mesh.name, "joints", len(joint_data), ["JOINT"], "name")

        # Add bind poses
        bind_data = self.data.scene.skeleton.inverse_bind_matrices(transpose=False)
        bind_source = utils.create_source(skin, mesh.name, "bindposes", bind_data, count=len(bind_data) * 16)
        utils.add_accessor(bind_source, mesh.name, "bindposes", len(bind_data), ["TRANSFORM"], "float4x4", 16)

        # Add weights
        weight_source = utils.create_source(skin, mesh.name, "weights", mesh.links_weights.flatten())
        utils.add_accessor(weight_source, mesh.name, "weights", len(mesh.links_weights), ["WEIGHT"], "float")

    def _add_joints_and_weights(self, mesh: ModelMesh, skin: Element):
        # Add joints
        joints = SubElement(skin, "joints")
        SubElement(joints, "input", semantic="JOINT", source=f"#{mesh.name}-joints")
        SubElement(joints, "input", semantic="INV_BIND_MATRIX", source=f"#{mesh.name}-bindposes")

        # Add vertex weights
        weights = SubElement(skin, "vertex_weights", count=str(mesh.count.vertices))
        SubElement(weights, "input", semantic="JOINT", source=f"#{mesh.name}-joints", offset="0")
        SubElement(weights, "input", semantic="WEIGHT", source=f"#{mesh.name}-weights", offset="1")

        # Add indices
        weight_index = itertools.count()
        bone_indices = [f"{bone_id} {next(weight_index)}" for bone_id in mesh.links_ids.flatten()]

        SubElement(weights, "vcount").text = " ".join(["4"] * mesh.count.vertices)
        SubElement(weights, "v").text = " ".join(bone_indices)

    def _add_scenes(self):
        library = SubElement(self.ctx["ROOT"], "library_visual_scenes")
        visual_scene = SubElement(library, "visual_scene", id="scene", name="Scene")

        if self._skeleton_presented:
            visual_scene = self._add_armature(visual_scene)

        self._add_mesh_instances(visual_scene)

        scene = SubElement(self.ctx["ROOT"], "scene")
        SubElement(scene, "instance_visual_scene", url="#scene")

    def _add_armature(self, scene: Element) -> Element:
        node = SubElement(scene, "node", id="armature", name="Armature", type="NODE")
        SubElement(node, "matrix", sid="transform").text = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

        for root in self.data.scene.skeleton.roots:
            self._add_bone(node, root)

        return node

    def _add_bone(self, parent: Element, bone: "SkeletonBone"):
        joint = SubElement(parent, "node", id=f"armature-{bone.name}", sid=bone.name, name=bone.name, type="JOINT")

        matrix = create_transform_matrix(bone.position, bone.rotation)
        SubElement(joint, "matrix", sid="transform").text = " ".join(map(str, matrix.flatten()))

        for child in bone.children:
            self._add_bone(joint, child)

    def _add_mesh_instances(self, parent: Element):
        for mesh in self.data.scene.meshes:
            node = SubElement(parent, "node", id=mesh.name, name=mesh.name, type="NODE")

            if self._skeleton_presented:
                bone = self.data.scene.skeleton.roots[0]
                instance = SubElement(node, "instance_controller", url=f"#{mesh.name}-skin")
                SubElement(instance, "skeleton").text = f"#armature-{bone.name}"
            else:
                instance = SubElement(node, "instance_geometry", url=f"#{mesh.name}", name=mesh.name)

            self._add_bind_material(mesh, instance)

    def _add_bind_material(self, mesh: ModelMesh, instance: Element):
        bind = SubElement(instance, "bind_material")
        technique_common = SubElement(bind, "technique_common")
        SubElement(
            technique_common,
            "instance_material",
            symbol=f"{mesh.material}-material",
            target=f"#{mesh.material}-material",
        )
