"""
Scene transformation functions.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import replace
from typing import TYPE_CHECKING

import numpy as np

from scfile.exceptions import AnimationError
from scfile.structures.models.animation import AnimationClip

from .enums import AnimationTranslation, LinkSpace, SkeletonSpace, UVOrigin, UVSign
from .matrices import create_transform_matrix
from .mesh import ModelMesh
from .scene import ModelScene, ModelSkin
from .skeleton import ModelSkeleton, SkeletonBone
from .types import BindPose, InverseBindMatrices, TransformMatrix


if TYPE_CHECKING:
    from scfile.core.content import ModelContent


type SceneTransform = Callable[[ModelScene], ModelScene]
type ModelTransform = Callable[["ModelContent"], "ModelContent"]
type AnimationTransform = Callable[[ModelScene, ModelScene], ModelScene]


def scene_transforms(
    *transforms: SceneTransform,
) -> tuple[ModelTransform, ...]:
    """Adapt scene transformations to model content."""

    def adapt(transform: SceneTransform) -> ModelTransform:
        def apply(data: ModelContent) -> ModelContent:
            return replace(data, scene=transform(data.scene))

        return apply

    return tuple(adapt(transform) for transform in transforms)


def unique_names(scene: ModelScene) -> ModelScene:
    """Ensure all meshes have unique names."""

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
    """Flip V axis (TOP_LEFT → BOTTOM_LEFT)."""

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
    """Invert V axis sign (POSITIVE → NEGATIVE)."""

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


def global_transforms(skeleton: ModelSkeleton) -> BindPose:
    """Compute global transformation matrices for a valid skeleton."""

    bones = skeleton.bones
    cache: list[TransformMatrix | None] = [None] * len(bones)

    def resolve(index: int) -> TransformMatrix:
        if (matrix := cache[index]) is not None:
            return matrix

        bone = bones[index]
        matrix = create_transform_matrix(bone.position, bone.rotation)

        if not bone.is_root:
            matrix = resolve(bone.parent_id) @ matrix

        cache[index] = matrix
        return matrix

    return [resolve(index) for index in range(len(bones))]


def inverse_bind_matrices(
    skeleton: ModelSkeleton,
    *,
    transpose: bool = False,
) -> InverseBindMatrices:
    """Compute inverse bind matrices for a valid skeleton."""

    matrices = [np.linalg.inv(matrix) for matrix in global_transforms(skeleton)]

    if not matrices:
        return np.empty((0, 4, 4), dtype=np.float32)

    if transpose:
        matrices = [matrix.T for matrix in matrices]

    return np.array(matrices, dtype=np.float32)


def skeleton_to_local(scene: ModelScene) -> ModelScene:
    """Convert bone positions (GLOBAL → LOCAL)."""

    if scene.skeleton.space == SkeletonSpace.LOCAL:
        return scene

    new_bones: list[SkeletonBone] = []

    for bone in scene.skeleton.bones:
        new_bone = replace(bone)
        new_bone.position = bone.position.copy()

        if not bone.is_root:
            new_bone.position -= scene.skeleton.bones[bone.parent_id].position

        new_bones.append(new_bone)

    new_skeleton = replace(scene.skeleton, bones=new_bones, space=SkeletonSpace.LOCAL)
    return replace(scene, skeleton=new_skeleton)


def animation_to_absolute(scene: ModelScene) -> ModelScene:
    """Add rest pose positions to animation deltas (DELTA → ABSOLUTE)."""

    if scene.animation.translation == AnimationTranslation.ABSOLUTE:
        return scene

    skeleton = scene.skeleton
    positions = np.array([bone.position for bone in skeleton.bones], dtype=np.float32)
    new_clips: list[AnimationClip] = []

    for clip in scene.animation.clips:
        if not clip.translations.size:
            new_clips.append(clip)
            continue

        new_translations = clip.translations.copy()
        new_translations += positions[np.newaxis, :, :]
        new_clips.append(replace(clip, translations=new_translations))

    new_animation = replace(
        scene.animation,
        clips=new_clips,
        translation=AnimationTranslation.ABSOLUTE,
    )
    return replace(scene, animation=new_animation)


def apply_fp_animation(animation: ModelScene, *models: ModelScene) -> ModelScene:
    """Combine model geometry with animation rig."""

    if not animation.animation.clips:
        raise AnimationError("Animation contains no clips.")

    if not models:
        raise AnimationError("No models provided.")

    target_ids = {bone.name: bone.id for bone in animation.skeleton.bones}
    if len(target_ids) != len(animation.skeleton.bones):
        raise AnimationError("Animation skeleton contains duplicate bone names.")

    meshes = list(animation.meshes)

    for model in models:
        for mesh in model.meshes:
            used_ids = {
                int(bone_id) for bone_id, weight in zip(mesh.links_ids.flat, mesh.links_weights.flat) if weight > 0.0
            }

            for source_id in used_ids:
                if source_id >= len(model.skeleton.bones):
                    raise AnimationError(f"Model references unknown bone {source_id}.")

                name = model.skeleton.bones[source_id].name
                if name not in target_ids:
                    raise AnimationError(f"Animation skeleton has no bone '{name}'.")

        source_ids = np.zeros(len(model.skeleton.bones), dtype=np.uint8)

        for bone in model.skeleton.bones:
            if bone.name in target_ids:
                source_ids[bone.id] = target_ids[bone.name]

        for mesh in model.meshes:
            new_mesh = replace(mesh)
            if mesh.max_influences:
                new_mesh.links_ids = source_ids[mesh.links_ids]
                new_mesh.link_space = LinkSpace.GLOBAL
            meshes.append(new_mesh)

    return replace(animation, meshes=meshes)


def apply_skins(scene: ModelScene, animation: ModelScene, *models: ModelScene) -> ModelScene:
    """Apply source bind poses to the assembled scene."""

    target_bones = animation.skeleton.bones
    target_ids = {bone.name: bone.id for bone in target_bones}
    target_scene = skeleton_to_local(animation)
    target_bind = inverse_bind_matrices(target_scene.skeleton)

    skins: list[InverseBindMatrices] = []
    mesh_skins: list[int | None] = []

    # Preserve source bind poses against the shared animation skeleton
    for model in (animation, *models):
        skinned = any(mesh.max_influences for mesh in model.meshes)
        skin_index = len(skins) if skinned else None

        if skinned:
            bind = target_bind.copy()
            source_scene = skeleton_to_local(model)
            source_bind = inverse_bind_matrices(source_scene.skeleton)

            # Keep target matrices for bones absent from this model
            for bone in model.skeleton.bones:
                if bone.name in target_ids:
                    bind[target_ids[bone.name]] = source_bind[bone.id]

            skins.append(bind)

        mesh_skins.extend(skin_index if mesh.max_influences else None for mesh in model.meshes)

    meshes = [replace(mesh, skin=skin) for mesh, skin in zip(scene.meshes, mesh_skins)]
    return replace(scene, meshes=meshes, skins=[ModelSkin(bind) for bind in skins])


def apply_animation_library(library: ModelScene, model: ModelScene) -> ModelScene:
    """Apply index-mapped skeletal animation clips to model."""

    if not library.animation.clips:
        raise AnimationError("Animation library contains no clips.")

    clips = library.animation.clips
    clip_bones = clips[0].translations.shape[1]
    model_bones = len(model.skeleton.bones)
    if clip_bones != model_bones:
        raise AnimationError(f"Animation library has {clip_bones} bones, model has {model_bones}.")

    return replace(model, animation=replace(library.animation))


def apply_morph_animation(animation: ModelScene, model: ModelScene) -> ModelScene:
    """Apply morph animation clips to compatible model blend shapes."""

    clips = animation.animation.clips
    channels = animation.animation.morph_channels

    if not clips or not any(clip.morph_weights.size for clip in clips):
        raise AnimationError("Animation contains no morph clips.")

    if len(set(channels)) != len(channels):
        raise AnimationError("Animation contains duplicate morph channel names.")

    mapped = {shape.channel for mesh in model.meshes for shape in mesh.blend_shapes if shape.channel is not None}
    if not mapped:
        raise AnimationError("Model contains no mapped blend shapes.")

    if not mapped.intersection(channels):
        raise AnimationError("Animation has no channels compatible with model blend shapes.")

    return replace(model, animation=replace(animation.animation))
