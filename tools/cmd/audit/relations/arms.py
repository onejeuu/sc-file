from functools import partial
from pathlib import Path

import numpy as np

from scfile import formats
from scfile.exceptions import AnimationError
from scfile.options import Options
from scfile.structures.models import AnimationClip, ModelScene
from scfile.structures.models import transforms as T
from tools.cmd.audit import mappings
from tools.cmd.audit.runner import Case, Plan, PlanError, Suite, Warning
from tools.cmd.audit.schemas import Arms, Record


KIND = "arms"
NAME = "mcvd+mcsb (arms)"

ANIMATIONS = Path("highpoly/animations")
HANDS = Path("highpoly/character_hands.mcsb")

OPTIONS = Options(skeleton=True, animation=True)


def _clip_moves(clip: AnimationClip) -> bool:
    if clip.frames < 2:
        return False

    if clip.translations.size and not np.allclose(clip.translations, clip.translations[:1], rtol=0.0, atol=1e-6):
        return True

    if clip.rotations.size:
        rotations = clip.rotations.astype(np.float64)
        norms = np.linalg.norm(rotations, axis=2, keepdims=True)
        rotations = np.divide(rotations, norms, out=np.zeros_like(rotations), where=norms != 0.0)
        similarity = np.abs(np.sum(rotations * rotations[:1], axis=2))
        if np.any(similarity < 1.0 - 1e-6):
            return True

    return bool(
        clip.morph_weights.size
        and not np.allclose(clip.morph_weights, clip.morph_weights[:1], rtol=0.0, atol=1e-6)
    )


def _validate_result(source: ModelScene, models: list[ModelScene], scene: ModelScene) -> None:
    expected_meshes = len(source.meshes) + sum(len(model.meshes) for model in models)
    if len(scene.meshes) != expected_meshes:
        raise AnimationError(f"Assembled scene lost {expected_meshes - len(scene.meshes)} meshes.")

    target_names = {bone.name for bone in scene.skeleton.bones}
    for model in models:
        used_ids = {
            int(bone_id)
            for mesh in model.meshes
            for bone_id, weight in zip(mesh.links_ids.flat, mesh.links_weights.flat)
            if weight > 0.0
        }
        missing = {model.skeleton.bones[bone_id].name for bone_id in used_ids} - target_names
        if missing:
            names = ", ".join(sorted(missing))
            raise AnimationError(f"Assembled skeleton lost model bones: {names}.")

    bones = len(scene.skeleton.bones)
    for clip in scene.animation.clips:
        if clip.translations.size and clip.translations.shape != (clip.frames, bones, 3):
            raise AnimationError(f"Animation clip '{clip.name}' does not cover the assembled skeleton.")
        if clip.rotations.size and clip.rotations.shape != (clip.frames, bones, 4):
            raise AnimationError(f"Animation clip '{clip.name}' does not cover the assembled skeleton.")

    if not any(_clip_moves(clip) for clip in scene.animation.clips):
        raise AnimationError("Animation contains no moving clips.")


def validate(root: Path, animation: Path, weapon: Path | None, hands: Path) -> list[Record]:
    with formats.McvdDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    contents = []
    for path in filter(None, (weapon, hands)):
        with formats.McsbDecoder(path, OPTIONS) as decoder:
            contents.append(decoder.decode())

    models = [model.scene for model in contents]
    scene = T.apply_fp_models(source.scene, *models)
    _validate_result(source.scene, models, scene)
    clips = scene.animation.clips
    record = Arms(
        animation=animation.relative_to(root).as_posix(),
        model=(weapon or hands).relative_to(root).as_posix(),
        clips=len(clips),
        frames=sum(clip.frames for clip in clips),
        bones=len(scene.skeleton.bones),
        meshes=len(scene.meshes),
        vertices=scene.total_vertices,
        polygons=scene.total_polygons,
    )
    return [record]


def build(root: Path) -> Plan:
    animations = sorted((root / ANIMATIONS).glob("*.mcvd"))
    hands = root / HANDS
    if not hands.is_file():
        raise PlanError(f"Shared hands model does not exist: {HANDS.as_posix()}")

    value = mappings.read(KIND)
    linked = mappings.animations(KIND)
    available = {animation.relative_to(root).as_posix().casefold(): animation for animation in animations}
    warnings = []
    cases = []

    for relative, models in linked.items():
        animation = available.pop(relative.casefold(), root / relative)
        if not animation.is_file():
            warnings.append(Warning(KIND, {"animation": animation}, "Mapped animation does not exist."))
            continue

        if not models:
            warnings.append(Warning(KIND, {"animation": animation}, "Animation has no mapped models."))
            continue

        for relative_model in models:
            model = root / relative_model
            if not model.is_file():
                warnings.append(Warning(KIND, {"animation": animation, "model": model}, "Mapped model does not exist."))
                continue
            cases.append(
                Case(
                    {"animation": animation, "model": model, "hands": hands},
                    partial(validate, root, animation, model, hands),
                    files=2,
                )
            )

    for relative in value.get("hands_only", []):
        animation = available.pop(relative.casefold(), root / relative)
        if not animation.is_file():
            warnings.append(Warning(KIND, {"animation": animation}, "Mapped animation does not exist."))
            continue
        cases.append(
            Case(
                {"animation": animation, "hands": hands},
                partial(validate, root, animation, None, hands),
                files=2,
            )
        )

    for excluded in value.get("excluded", []):
        available.pop(excluded["animation"].casefold(), None)

    warnings.extend(
        Warning(KIND, {"animation": animation}, "Animation has no mapping.") for animation in available.values()
    )

    suite = Suite(KIND, NAME, cases)
    return Plan([suite], warnings)
