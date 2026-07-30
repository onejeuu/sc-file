"""
External model animation.
"""

from dataclasses import replace
from pathlib import Path
from typing import Callable, TypeAlias

from scfile import exceptions, formats, types
from scfile.core import ModelContent, Options
from scfile.core.types import ModelDecoder
from scfile.structures import models as S
from scfile.structures.models import transforms as T

from .conversion import destination, validate_sources


MODELS_LIMIT = 8
AnimationTransform: TypeAlias = Callable[[S.ModelScene, S.ModelScene], S.ModelScene]


def _apply_external(
    decoder: ModelDecoder,
    transform: AnimationTransform,
    animation: types.PathLike,
    model: types.PathLike,
    output: types.OutputLike = None,
) -> Path:
    animation_path, model_path = validate_sources(animation, model)
    output_path = destination(animation_path, output, formats.GlbEncoder.format.suffix)
    options = Options(skeleton=True, animation=True)

    with decoder(animation_path, options) as source:
        animation_data = source.decode()

    with formats.McsbDecoder(model_path, options) as mcsb:
        model_data = mcsb.decode()

    scene = transform(animation_data.scene, model_data.scene)
    data = replace(model_data, scene=scene)

    with formats.GlbEncoder(data, options) as glb:
        glb.save(output_path)

    return output_path


def _skin_context(
    animation: ModelContent,
    *models: ModelContent,
) -> tuple[list[S.InverseBindMatrices], list[int | None]]:
    target_bones = animation.scene.skeleton.bones
    target_ids = {bone.name: bone.id for bone in target_bones}
    target_scene = T.skeleton_to_local(animation.scene)
    target_bind = target_scene.skeleton.inverse_bind_matrices(transpose=False)

    skins: list[S.InverseBindMatrices] = []
    mesh_skins: list[int | None] = []

    # Preserve source bind poses against the shared animation skeleton
    for model in (animation, *models):
        skinned = any(mesh.max_influences for mesh in model.scene.meshes)
        skin_index = len(skins) if skinned else None

        if skinned:
            bind = target_bind.copy()
            source_scene = T.skeleton_to_local(model.scene)
            source_bind = source_scene.skeleton.inverse_bind_matrices(transpose=False)

            # Keep target matrices for bones absent from this model
            for bone in model.scene.skeleton.bones:
                if bone.name in target_ids:
                    bind[target_ids[bone.name]] = source_bind[bone.id]

            skins.append(bind)

        mesh_skins.extend(skin_index if mesh.max_influences else None for mesh in model.scene.meshes)

    return skins, mesh_skins


def arms(
    animation: types.PathLike,
    *models: types.PathLike,
    output: types.OutputLike = None,
) -> Path:
    """Apply first-person animation to weapon and hands models."""

    if not models:
        raise exceptions.AnimationError("No models provided.")

    if len(models) > MODELS_LIMIT:
        raise exceptions.AnimationError(f"Too many models: {len(models)} (max: {MODELS_LIMIT}).")

    animation_path, *model_paths = validate_sources(animation, *models)
    output_path = destination(animation_path, output, formats.GlbEncoder.format.suffix)
    options = Options(skeleton=True, animation=True)

    with formats.McvdDecoder(animation_path, options) as mcvd:
        animation_data = mcvd.decode()

    model_data = []
    for model_path in model_paths:
        with formats.McsbDecoder(model_path, options) as mcsb:
            model_data.append(mcsb.decode())

    scene = T.apply_animation(animation_data.scene, *(model.scene for model in model_data))
    data = replace(animation_data, scene=scene)
    skins, mesh_skins = _skin_context(animation_data, *model_data)

    with formats.GlbEncoder(data, options) as glb:
        glb.ctx["SKINS"] = skins
        glb.ctx["MESH_SKINS"] = mesh_skins
        glb.save(output_path)

    return output_path


def face(
    animation: types.PathLike,
    model: types.PathLike,
    output: types.OutputLike = None,
) -> Path:
    """Apply facial animation to a head model."""

    return _apply_external(
        formats.McvdDecoder,
        T.apply_morph_animation,
        animation,
        model,
        output,
    )


def body(
    library: types.PathLike,
    model: types.PathLike,
    output: types.OutputLike = None,
) -> Path:
    """Apply animation library to a model."""

    return _apply_external(
        formats.McalDecoder,
        T.apply_animation_library,
        library,
        model,
        output,
    )
