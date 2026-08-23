from functools import partial
from pathlib import Path

from scfile import formats
from scfile.content import ModelContent
from scfile.content.models import transforms as T
from scfile.options import Options
from tools.cmd.audit import mappings
from tools.cmd.audit.runner import Case, Plan, Suite, Warning
from tools.cmd.audit.schemas import Face, Record


KIND = "face"
NAME = "mcvd+mcsb (face)"

OPTIONS = Options(skeleton=True, animation=True)


def decode(animation: Path, model: Path) -> tuple[ModelContent, ModelContent]:
    with formats.McvdDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    with formats.McsbDecoder(model, OPTIONS) as decoder:
        target = decoder.decode()

    return source, target


def validate(root: Path, animation: Path, model: Path) -> list[Record]:
    source, target = decode(animation, model)
    scene = T.apply_morph_animation(source.scene, target.scene)
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
    value = mappings.read(KIND)
    cases = []
    warnings = []
    seen: set[tuple[Path, Path]] = set()

    def add(animation: Path, model: Path) -> None:
        pair = animation, model
        if pair in seen:
            return
        seen.add(pair)
        cases.append(
            Case(
                {"animation": animation, "model": model},
                partial(validate, root, animation, model),
                files=2,
            )
        )

    for group in value.get("dynamic", []):
        animations = sorted((root / group["animations"]).rglob("*.mcvd"))
        models = []
        for relative in group["models"]:
            model = root / relative
            if model.is_file():
                models.append(model)
            else:
                warnings.append(Warning(KIND, {"model": model}, "Mapped head model does not exist."))

        if not animations:
            warnings.append(Warning(KIND, {"animation": root / group["animations"]}, "Mapped animation path is empty."))
            continue

        if not models:
            warnings.append(Warning(KIND, {}, "Dynamic facial mapping has no available models."))
            continue

        reference = group["reference"]
        animation = root / reference["animation"]
        model = root / reference["model"]

        if animation not in animations:
            warnings.append(Warning(KIND, {"animation": animation}, "Reference animation does not exist."))
            animation = animations[0]

        if model not in models:
            warnings.append(Warning(KIND, {"model": model}, "Reference head model does not exist."))
            model = models[0]

        for head in models:
            add(animation, head)

        for source in animations:
            add(source, model)

    for relative, models in mappings.animations(KIND).items():
        animation = root / relative
        if not animation.is_file():
            warnings.append(Warning(KIND, {"animation": animation}, "Mapped facial animation does not exist."))
            continue

        for relative_model in models:
            model = root / relative_model
            if model.is_file():
                add(animation, model)
            else:
                warnings.append(
                    Warning(KIND, {"animation": animation, "model": model}, "Mapped head model does not exist.")
                )

    return Plan([Suite(KIND, NAME, cases)], warnings)
