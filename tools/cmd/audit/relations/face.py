from functools import partial
from pathlib import Path

from scfile import formats
from scfile.options import Options
from scfile.structures.content import ModelContent
from scfile.structures.models import transforms
from tools.cmd.audit import rules
from tools.cmd.audit.runner import Case, Plan, PlanError, Suite
from tools.cmd.audit.schemas import Face, Record


KIND = "face"
NAME = "mcvd+mcsb (face)"

ANIMATIONS = Path("highpoly/lipsync")
MODELS = Path("stalkerplayer/heads")

OPTIONS = Options(model=Options.Model(skeleton=True, animation=True))


def decode(animation: Path, model: Path) -> tuple[ModelContent, ModelContent]:
    with formats.McvdDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    with formats.McsbDecoder(model, OPTIONS) as decoder:
        target = decoder.decode()

    return source, target


def validate(root: Path, animation: Path, model: Path) -> list[Record]:
    source, target = decode(animation, model)
    scene = transforms.apply_morph_animation(source.scene, target.scene)
    clips = source.scene.animation.clips
    channels = set(source.scene.animation.morph_channels)
    shapes = [shape for mesh in target.scene.meshes for shape in mesh.blend_shapes]
    mapped = {shape.channel for shape in shapes if shape.channel in channels}

    return [
        Face(
            animation=animation.relative_to(root).as_posix(),
            model=model.relative_to(root).as_posix(),
            clips=len(clips),
            frames=sum(clip.frames for clip in clips),
            channels=len(channels),
            shapes=len(shapes),
            mapped=len(mapped),
            meshes=len(scene.meshes),
            vertices=scene.total_vertices,
            polygons=scene.total_polygons,
        )
    ]


def build(root: Path) -> Plan:
    animations = sorted((root / ANIMATIONS).rglob("*.mcvd"))
    models = sorted((root / MODELS).rglob("*.mcsb"))
    animation = root / rules.FACE_ANIMATION
    model = root / rules.FACE_MODEL

    if animation not in animations:
        raise PlanError(f"Reference facial animation does not exist: {rules.FACE_ANIMATION}")
    if model not in models:
        raise PlanError(f"Reference head model does not exist: {rules.FACE_MODEL}")

    cases = [
        Case(
            {"animation": animation, "model": head},
            partial(validate, root, animation, head),
            files=2 if head == model else 1,
        )
        for head in models
    ]
    cases.extend(
        Case(
            {"animation": source, "model": model},
            partial(validate, root, source, model),
        )
        for source in animations
        if source != animation
    )

    return Plan([Suite(KIND, NAME, cases)])
