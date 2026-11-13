"""Model animation operations."""

from dataclasses import replace
from hashlib import blake2b
from typing import overload

from scfile import formats, types
from scfile.content import ModelContent
from scfile.content.models import AnimationClip
from scfile.content.models import transforms as T
from scfile.core import ModelDecoder, Resources
from scfile.io.models import ModelReader
from scfile.options import Options

from . import paths


@overload
def arms(
    animation: types.SourceLike,
    weapon: types.SourceLike,
    hands: types.SourceLike | None = None,
    output: types.OutputLike = None,
    options: Options | None = None,
    resources: Resources | None = None,
) -> types.ResultPath: ...


@overload
def arms(
    animation: types.SourceLike,
    weapon: None = None,
    *,
    hands: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
    resources: Resources | None = None,
) -> types.ResultPath: ...


def arms(
    animation: types.SourceLike,
    weapon: types.SourceLike | None = None,
    hands: types.SourceLike | None = None,
    output: types.OutputLike = None,
    options: Options | None = None,
    resources: Resources | None = None,
) -> types.ResultPath:
    """
    Apply first person animation to weapon and hands models.

    Args:
        animation: First person animation source.
        weapon: Weapon model source.
        hands: Hands model source.
        output (optional): Output file or directory.
        options (optional): Animation and conversion options.
        resources (optional): Resources shared by handlers in this operation.

    Returns:
        Output path on success, or ``None`` when output is skipped.
    """

    encoder = formats.GlbEncoder
    options = _options(options)
    resources = resources if resources is not None else Resources()

    src = paths.source(animation)
    out = paths.output(src, output, encoder.suffix(), options)
    if not out:
        return

    with formats.McvdDecoder(src, options, resources) as mcvd:
        anims = mcvd.decode()

    sources = tuple(filter(None, (weapon, hands)))
    models: list[ModelContent] = []

    for source in sources:
        with formats.McsbDecoder(paths.source(source), options, resources) as mcsb:
            models.append(mcsb.decode())

    scene = T.apply_fp_models(anims.scene, *(model.scene for model in models))
    content = replace(anims, scene=scene)

    with paths.stage(out) as tmp:
        with encoder(content, options, output=tmp, resources=resources) as glb:
            glb.encode()

    return out


def body(
    animation: types.SourceLike,
    model: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
    resources: Resources | None = None,
) -> types.ResultPath:
    """
    Apply skeletal animation to a model.

    Args:
        animation: Skeletal animation source.
        model: Origin model source.
        output (optional): Output file or directory.
        options (optional): Animation and conversion options.
        resources (optional): Resources shared by handlers in this operation.

    Returns:
        Output path on success, or ``None`` when output is skipped.
    """

    return _apply_external_animation(
        decoder=formats.McalDecoder,
        transform=T.apply_skeletal_animation,
        animation=animation,
        model=model,
        output=output,
        options=options,
        resources=resources,
    )


def face(
    animation: types.SourceLike,
    model: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
    resources: Resources | None = None,
) -> types.ResultPath:
    """
    Apply facial animation to a head model.

    Args:
        animation: Facial animation source.
        model: Head model source.
        output (optional): Output file or directory.
        options (optional): Animation and conversion options.
        resources (optional): Resources shared by handlers in this operation.

    Returns:
        Output path on success, or ``None`` when output is skipped.
    """

    return _apply_external_animation(
        decoder=formats.McvdDecoder,
        transform=T.apply_morph_animation,
        animation=animation,
        model=model,
        output=output,
        options=options,
        resources=resources,
    )


def _options(
    options: Options | None,
) -> Options:
    return replace(options if options is not None else Options(), skeleton=True, animation=True)


def _apply_external_animation(
    decoder: type[ModelDecoder[ModelReader]],
    transform: T.AnimationTransform,
    animation: types.SourceLike,
    model: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
    resources: Resources | None = None,
) -> types.ResultPath:
    encoder = formats.GlbEncoder
    options = _options(options)
    resources = resources if resources is not None else Resources()

    src = paths.source(animation)
    mdl = paths.source(model)
    out = paths.output(src, output, encoder.suffix(), options)
    if not out:
        return

    with decoder(src, options, resources) as dec:
        anims = dec.decode()

    if decoder is formats.McalDecoder and not options.mcal_extended:
        library = anims.scene.animation
        scene = replace(anims.scene, animation=replace(library, clips=_filter_clips(library.clips)))
        anims = replace(anims, scene=scene)

    with formats.McsbDecoder(mdl, options, resources) as mcsb:
        target = mcsb.decode()

    scene = transform(anims.scene, target.scene)
    content = replace(target, scene=scene)

    with paths.stage(out) as tmp:
        with encoder(content, options, output=tmp, resources=resources) as glb:
            glb.encode()

    return out


def _filter_clips(clips: list[AnimationClip]) -> list[AnimationClip]:
    filtered: dict[bytes, AnimationClip] = {}

    for clip in clips:
        name = clip.name.casefold()
        static = all(
            values.size == 0 or bool((values == values[:1]).all())
            for values in (
                clip.translations,
                clip.rotations,
                clip.morph_weights,
            )
        )
        technical = name.endswith("_layer") or "_cluster_" in name
        control = "_turn" in name or "_look_" in name or "_aim_point_" in name
        if technical or static and control:
            continue

        key = blake2b(digest_size=16)
        key.update(clip.frames.to_bytes(4, "little"))
        key.update(clip.rate.hex().encode())
        for values in (clip.translations, clip.rotations, clip.morph_weights):
            key.update(values)
        filtered.setdefault(key.digest(), clip)

    return list(filtered.values())
