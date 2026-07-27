"""
Model animation export.
"""

from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Optional

from scfile import exceptions, formats, types
from scfile.core import ModelContent, Options
from scfile.structures import models as S
from scfile.structures.models import transforms as T

from .convert import ensure_unique_path


ANIMATION_MODELS_LIMIT = 8


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

        # Match merged mesh order from apply_animation()
        mesh_skins.extend(skin_index if mesh.max_influences else None for mesh in model.scene.meshes)

    return skins, mesh_skins


def animate(
    animation: types.PathLike,
    *models: types.PathLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> None:
    """Export model geometry with MCVD animations to GLB."""

    animation_path = Path(animation)
    model_paths = [Path(model) for model in models]

    if not model_paths:
        raise exceptions.AnimationError("No models provided.")

    if len(model_paths) > ANIMATION_MODELS_LIMIT:
        raise exceptions.AnimationError(f"Too many models: {len(model_paths)} (max: {ANIMATION_MODELS_LIMIT}).")

    for path in (animation_path, *model_paths):
        if not path.exists() or not path.is_file():
            raise exceptions.FileNotFound(str(path))

    out_path = Path(output or animation_path.parent)
    out_format = formats.GlbEncoder.format

    if out_path.suffix == out_format.suffix:
        out_dir = out_path.parent
        out_name = out_path.name
    else:
        out_dir = out_path
        out_name = f"{animation_path.stem}{out_format.suffix}"

    out_dir.mkdir(exist_ok=True, parents=True)
    output_path = out_dir / out_name

    options = replace(options or Options(), skeleton=True, animation=True)

    match options.on_conflict:
        case "skip" if output_path.exists():
            return
        case "rename":
            output_path = ensure_unique_path(output_path)

    # Decode animation and geometry sources
    with formats.McvdDecoder(animation_path, options) as mcvd:
        animation_data = mcvd.decode()

    model_data = []
    for model_path in model_paths:
        with formats.McsbDecoder(model_path, options) as mcsb:
            model_data.append(mcsb.decode())

    # Combine content while preserving bind poses for each source
    flags: S.ModelFlags = defaultdict(bool, animation_data.flags)
    for model in model_data:
        for flag, enabled in model.flags.items():
            flags[flag] |= enabled

    scene = T.apply_animation(animation_data.scene, *(model.scene for model in model_data))
    data = replace(animation_data, flags=flags, scene=scene)
    skins, mesh_skins = _skin_context(animation_data, *model_data)

    with formats.GlbEncoder(data, options) as glb:
        glb.ctx["SKINS"] = skins
        glb.ctx["MESH_SKINS"] = mesh_skins
        glb.save(output_path)
