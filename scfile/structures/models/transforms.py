from dataclasses import replace
from typing import Callable, TypeAlias

import numpy as np

from scfile.consts import ModelDefaults
from scfile.structures.models.animation import AnimationClip

from .enums import AnimationTranslation, SkeletonHierarchy, SkeletonSpace, UVOrigin, UVSign
from .mesh import ModelMesh
from .scene import ModelScene
from .skeleton import SkeletonBone


SceneTransform: TypeAlias = Callable[[ModelScene], ModelScene]


def unique_names(scene: ModelScene) -> ModelScene:
    seen_names: set[str] = set()
    meshes: list[ModelMesh] = []

    for mesh in scene.meshes:
        name = mesh.name or "noname"

        base_name, count = name, 2
        unique_name = f"{base_name}"

        while unique_name in seen_names:
            unique_name = f"{base_name}_{count}"
            count += 1

        seen_names.add(unique_name)
        meshes.append(replace(mesh, name=unique_name))

    return replace(scene, meshes=meshes)


def flip_uv(scene: ModelScene) -> ModelScene:
    meshes: list[ModelMesh] = []

    for mesh in scene.meshes:
        if mesh.uv_origin == UVOrigin.BOTTOM_LEFT and mesh.uv_sign == UVSign.POSITIVE:
            meshes.append(mesh)
            continue

        new_mesh = replace(mesh)
        new_mesh.uv1 = mesh.uv1.copy()
        new_mesh.uv2 = mesh.uv2.copy()
        new_mesh.uv1[:, 1] = 1.0 - new_mesh.uv1[:, 1]
        new_mesh.uv2[:, 1] = 1.0 - new_mesh.uv2[:, 1]
        new_mesh.uv_origin = UVOrigin.BOTTOM_LEFT
        new_mesh.uv_sign = UVSign.POSITIVE
        meshes.append(new_mesh)

    return replace(scene, meshes=meshes)


def invert_uv(scene: ModelScene) -> ModelScene:
    meshes: list[ModelMesh] = []

    for mesh in scene.meshes:
        if mesh.uv_sign == UVSign.NEGATIVE:
            meshes.append(mesh)
            continue

        new_mesh = replace(mesh)
        new_mesh.uv1 = mesh.uv1.copy()
        new_mesh.uv2 = mesh.uv2.copy()
        new_mesh.uv1[:, 1] *= -1.0
        new_mesh.uv2[:, 1] *= -1.0
        new_mesh.uv_sign = UVSign.NEGATIVE
        meshes.append(new_mesh)

    return replace(scene, meshes=meshes)


def skeleton_to_local(scene: ModelScene) -> ModelScene:
    if scene.skeleton.space == SkeletonSpace.LOCAL:
        return scene

    new_bones: list[SkeletonBone] = []

    for bone in scene.skeleton.bones:
        new_bone = replace(bone)
        new_bone.position = bone.position.copy()

        parent_id = bone.parent_id
        while parent_id > ModelDefaults.ROOT_BONE_ID:
            parent = new_bones[parent_id]
            new_bone.position -= parent.position
            parent_id = parent.parent_id

        new_bones.append(new_bone)

    new_skeleton = replace(scene.skeleton, bones=new_bones, space=SkeletonSpace.LOCAL)
    return replace(scene, skeleton=new_skeleton)


def build_hierarchy(scene: ModelScene) -> ModelScene:
    if scene.skeleton.hierarchy == SkeletonHierarchy.BUILT:
        return scene

    new_bones: list[SkeletonBone] = [replace(bone) for bone in scene.skeleton.bones]

    for bone in new_bones:
        if not bone.is_root:
            parent = new_bones[bone.parent_id]
            parent.children.append(bone)

    new_skeleton = replace(scene.skeleton, bones=new_bones, hierarchy=SkeletonHierarchy.BUILT)
    return replace(scene, skeleton=new_skeleton)


def animation_to_absolute(scene: ModelScene) -> ModelScene:
    if scene.animation.translation == AnimationTranslation.ABSOLUTE:
        return scene

    skeleton = scene.skeleton
    positions = np.array([bone.position for bone in skeleton.bones], dtype=np.float32)
    new_clips: list[AnimationClip] = []

    for clip in scene.animation.clips:
        new_translations = clip.translations.copy()
        new_translations += positions[np.newaxis, :, :]
        new_clips.append(replace(clip, translations=new_translations))

    new_animation = replace(
        scene.animation,
        clips=new_clips,
        translation=AnimationTranslation.ABSOLUTE,
    )
    return replace(scene, animation=new_animation)
