from functools import partial
from pathlib import Path

from scfile import formats
from scfile.options import Options
from scfile.structures.models import transforms
from tools.cmd.audit import rules
from tools.cmd.audit.runner import Case, Plan, PlanError, Suite, Warning
from tools.cmd.audit.schemas import Body, Record


KIND = "body"
NAME = "mcal+mcsb (body)"

OPTIONS = Options(model=Options.Model(skeleton=True, animation=True, raw_clips=True))


def models(root: Path, animation: Path) -> tuple[str, ...]:
    relative = animation.relative_to(root)
    for path in (relative, *relative.parents):
        if linked := rules.BODY_MODELS.get(path.as_posix()):
            return linked
    return ()


def validate(root: Path, animation: Path, model: Path) -> list[Record]:
    with formats.McalDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    with formats.McsbDecoder(model, OPTIONS) as decoder:
        target = decoder.decode()

    scene = transforms.apply_skeletal_animation(source.scene, target.scene)
    clips = scene.animation.clips
    return [
        Body(
            animation=animation.relative_to(root).as_posix(),
            model=model.relative_to(root).as_posix(),
            clips=len(clips),
            frames=sum(clip.frames for clip in clips),
            bones=len(scene.skeleton.bones),
            meshes=len(scene.meshes),
            vertices=scene.total_vertices,
            polygons=scene.total_polygons,
        )
    ]


def build(root: Path) -> Plan:
    animations = sorted(root.rglob("*.mcal"))
    if not animations:
        raise PlanError("No skeletal animations found.")

    cases = []
    warnings = []
    covered: set[Path] = set()

    for animation in animations:
        linked = models(root, animation)
        if not linked:
            warnings.append(Warning(KIND, {"animation": animation}, "No body model match."))
            continue

        for relative in linked:
            model = root / relative
            if not model.is_file():
                warnings.append(Warning(KIND, {"animation": animation}, f"Linked model does not exist: {relative}"))
                continue

            paths = {animation, model}
            cases.append(
                Case(
                    {"animation": animation, "model": model},
                    partial(validate, root, animation, model),
                    files=len(paths - covered),
                )
            )
            covered.update(paths)

    return Plan([Suite(KIND, NAME, cases)], warnings)
