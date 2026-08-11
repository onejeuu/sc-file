import os
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from scfile.core import ModelContent, ModelDecoder
from scfile.exceptions import AnimationError
from scfile.formats import McalDecoder, McsbDecoder, McvdDecoder
from scfile.io.models import ModelReader
from scfile.options import Options
from scfile.structures.models import transforms

from .types import Error, Relations, Result


_OPTIONS = Options(model=Options.Model(skeleton=True, animation=True))

ARMS = "mcvd+mcsb (arms)"
FACE = "mcvd+mcsb (face)"
BODY = "mcal+mcsb (body)"


def find(root: Path) -> Relations:
    arms = root / "highpoly" / "animations"
    face = root / "highpoly" / "lipsync"
    heads = root / "stalkerplayer" / "heads"
    hands = root / "highpoly" / "character_hands.mcsb"
    character = root / "highpoly" / "character"

    return Relations(
        hands=hands if hands.is_file() else None,
        arms=sorted(arms.glob("*.mcvd")) if arms.is_dir() else [],
        face=sorted(face.glob("*.mcvd")) if face.is_dir() else [],
        heads=sorted(heads.rglob("*.mcsb")) if heads.is_dir() else [],
        body=(
            # Avoid decoding large packs twice
            sorted(path for path in character.rglob("*.mcal") if path.name != "pack.mcal") if character.is_dir() else []
        ),
        models=sorted(character.glob("*.mcsb")) if character.is_dir() else [],
    )


def found(relations: Relations, formats: tuple[str, ...]) -> Counter:
    result: Counter = Counter()

    if {"mcsb", "mcvd"}.issubset(formats) and relations.hands:
        result[ARMS] = len(relations.arms)

    if {"mcsb", "mcvd"}.issubset(formats) and relations.face and relations.heads:
        result[FACE] = len(relations.face) + len(relations.heads)

    if {"mcal", "mcsb"}.issubset(formats) and relations.models:
        result[BODY] = len(relations.body)

    return result


def _error(path: Path, root: Path, error: Exception) -> Error:
    relative = os.path.relpath(path, root).replace("\\", "/")
    return Error(path=relative, error=f"{type(error).__name__}: {error}")


def _decode(
    path: Path,
    decoder: type[ModelDecoder[ModelReader]],
) -> ModelContent:
    with decoder(path, _OPTIONS) as source:
        return source.decode()


def _arms(relations: Relations, root: Path) -> Iterator[Result]:
    if not relations.hands or not relations.arms:
        return

    # Validate against the shared hands rig
    try:
        hands = _decode(relations.hands, McsbDecoder)
    except Exception as error:
        for animation in relations.arms:
            yield Result(ARMS, _error(animation, root, error))
        return

    for animation in relations.arms:
        try:
            data = _decode(animation, McvdDecoder)
            transforms.apply_fp_animation(data.scene, hands.scene)
            yield Result(ARMS)
        except Exception as error:
            yield Result(ARMS, _error(animation, root, error))


def _mapped_shape_count(data: ModelContent) -> int:
    return sum(shape.channel is not None for mesh in data.scene.meshes for shape in mesh.blend_shapes)


def _face_reference(paths: list[Path]) -> ModelContent | None:
    for path in paths:
        try:
            data = _decode(path, McvdDecoder)
            if any(clip.morph_weights.size for clip in data.scene.animation.clips):
                return data
        except Exception:
            continue

    return None


def _face(relations: Relations, root: Path) -> Iterator[Result]:
    if not relations.face or not relations.heads:
        return

    animation = _face_reference(relations.face)
    if animation is None:
        error = AnimationError("No valid face animation found.")
        for path in (*relations.heads, *relations.face):
            yield Result(FACE, _error(path, root, error))
        return

    target: ModelContent | None = None
    target_shapes = -1

    # Validate every head and retain the most complete compatible target
    for head in relations.heads:
        try:
            data = _decode(head, McsbDecoder)
            transforms.apply_morph_animation(animation.scene, data.scene)
            shapes = _mapped_shape_count(data)
            if shapes > target_shapes:
                target = data
                target_shapes = shapes
            yield Result(FACE)
        except Exception as error:
            yield Result(FACE, _error(head, root, error))

    if target is None:
        error = AnimationError("No compatible head model found.")
        for path in relations.face:
            yield Result(FACE, _error(path, root, error))
        return

    # Validate animations against the most complete compatible head
    for path in relations.face:
        try:
            data = _decode(path, McvdDecoder)
            transforms.apply_morph_animation(data.scene, target.scene)
            yield Result(FACE)
        except Exception as error:
            yield Result(FACE, _error(path, root, error))


def _body(relations: Relations, root: Path) -> Iterator[Result]:
    models = _models(relations.models)

    for path in relations.body:
        try:
            library = _decode(path, McalDecoder)
            if not any(_compatible_library(library, model) for model in models):
                raise AnimationError("Animation library has no compatible model.")
            yield Result(BODY)
        except Exception as error:
            yield Result(BODY, _error(path, root, error))


def _compatible_library(library: ModelContent, model: ModelContent) -> bool:
    try:
        transforms.apply_animation_library(library.scene, model.scene)
        return True
    except AnimationError:
        return False


def _models(paths: list[Path]) -> list[ModelContent]:
    result = []
    for path in paths:
        try:
            result.append(_decode(path, McsbDecoder))
        except Exception:
            continue
    return result


def validate(
    relations: Relations,
    root: Path,
    enabled: set[str],
) -> Iterator[Result]:
    if ARMS in enabled:
        yield from _arms(relations, root)
    if FACE in enabled:
        yield from _face(relations, root)
    if BODY in enabled:
        yield from _body(relations, root)
