"""
External model animation.
"""

from copy import replace
from hashlib import blake2b

from scfile import formats, types
from scfile.core import ModelDecoder
from scfile.io.models import ModelReader
from scfile.options import Options
from scfile.structures.content import ModelContent
from scfile.structures.models import AnimationClip
from scfile.structures.models import transforms as T

from . import paths


POSE_FRAMES = 2
TRANSITION_FRAMES = 16
TRANSITION_PARTS = ("_landing", "_turn_", "_look_", "_aim_point_")


def arms(
    animation: types.SourceLike,
    model: types.SourceLike,
    hands: types.SourceLike | None = None,
    output: types.OutputLike = None,
    options: Options | None = None,
) -> types.ResultPath:
    """Apply first-person animation to weapon and hands models."""

    encoder = formats.GlbEncoder
    options = _options(options)

    src = paths.source(animation)
    mdl = paths.source(model)
    out = paths.output(src, output, encoder.suffix(), options)

    if out is None:
        return

    with formats.McvdDecoder(src, options) as mcvd:
        anims = mcvd.decode()

    with formats.McsbDecoder(mdl, options) as mcsb:
        target = mcsb.decode()

    models: tuple[ModelContent, ...] = (target,)
    if hands is not None:
        with formats.McsbDecoder(paths.source(hands), options) as mcsb:
            models += (mcsb.decode(),)

    scene = T.apply_fp_animation(anims.scene, *(model.scene for model in models))
    scene = T.apply_skins(scene, anims.scene, *(model.scene for model in models))
    content = replace(anims, scene=scene)

    with paths.stage(out) as tmp:
        with encoder(content, options, output=tmp) as glb:
            glb.encode()

    return out


def body(
    library: types.SourceLike,
    model: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
) -> types.ResultPath:
    """Apply animation library to a model."""

    return _apply_external_animation(
        decoder=formats.McalDecoder,
        transform=T.apply_animation_library,
        animation=library,
        model=model,
        output=output,
        options=options,
    )


def face(
    animation: types.SourceLike,
    model: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
) -> types.ResultPath:
    """Apply facial animation to a head model."""

    return _apply_external_animation(
        decoder=formats.McvdDecoder,
        transform=T.apply_morph_animation,
        animation=animation,
        model=model,
        output=output,
        options=options,
    )


def _options(
    options: Options | None,
) -> Options:
    options = (options or Options()).copy()
    options.model.skeleton = True
    options.model.animation = True
    return options


def _apply_external_animation(
    decoder: type[ModelDecoder[ModelReader]],
    transform: T.AnimationTransform,
    animation: types.SourceLike,
    model: types.SourceLike,
    output: types.OutputLike = None,
    options: Options | None = None,
) -> types.ResultPath:
    encoder = formats.GlbEncoder
    options = _options(options)

    src = paths.source(animation)
    mdl = paths.source(model)
    out = paths.output(src, output, encoder.suffix(), options)

    if out is None:
        return

    with decoder(src, options) as dec:
        anims = dec.decode()

    if decoder is formats.McalDecoder and not options.model.raw_clips:
        anims = _filtered_library(anims)

    with formats.McsbDecoder(mdl, options) as mcsb:
        target = mcsb.decode()

    scene = transform(anims.scene, target.scene)
    content = replace(target, scene=scene)

    with paths.stage(out) as tmp:
        with encoder(content, options, output=tmp) as glb:
            glb.encode()

    return out


def _filtered_library(library: ModelContent) -> ModelContent:
    animation = library.scene.animation
    clips: list[AnimationClip] = []
    seen: set[bytes] = set()

    for clip in animation.clips:
        name = clip.name.casefold()
        short = clip.frames <= TRANSITION_FRAMES
        technical = clip.frames <= POSE_FRAMES or "_cluster_" in name or name.endswith("_layer")
        if technical or short and any(part in name for part in TRANSITION_PARTS):
            continue

        key = blake2b(digest_size=16)
        key.update(clip.frames.to_bytes(4, "little"))
        key.update(clip.rate.hex().encode())
        for values in (clip.translations, clip.rotations, clip.morph_weights):
            key.update(values)

        key = key.digest()
        if key in seen:
            continue

        seen.add(key)
        clips.append(clip)

    animation = replace(animation, clips=clips)
    return replace(library, scene=replace(library.scene, animation=animation))
