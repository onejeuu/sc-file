"""
External model animation.
"""

from copy import replace

from scfile import formats, types
from scfile.structures.content import ModelContent
from scfile.core import ModelDecoder
from scfile.io.models import ModelReader
from scfile.options import Options
from scfile.structures.models import transforms as T

from . import paths


def arms(
    animation: types.SourceLike,
    model: types.SourceLike,
    hands: types.SourceLike | None = None,
    output: types.OutputLike = None,
    options: Options | None = None,
) -> types.ResultPath:
    """Apply first-person animation to weapon and hands models."""

    options = _options(options)

    src = paths.source(animation)
    mdl = paths.source(model)
    out = paths.output(src, output, formats.GlbEncoder.suffix(), options)

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
        with formats.GlbEncoder(content, options, output=tmp) as glb:
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
    options = _options(options)

    src = paths.source(animation)
    mdl = paths.source(model)
    out = paths.output(src, output, formats.GlbEncoder.suffix(), options)

    if out is None:
        return

    with decoder(src, options) as dec:
        anims = dec.decode()

    with formats.McsbDecoder(mdl, options) as mcsb:
        target = mcsb.decode()

    scene = transform(anims.scene, target.scene)
    content = replace(target, scene=scene)

    with paths.stage(out) as tmp:
        with formats.GlbEncoder(content, options, output=tmp) as glb:
            glb.encode()

    return out
