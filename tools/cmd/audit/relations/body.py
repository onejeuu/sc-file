from functools import partial
from pathlib import Path

from scfile import formats
from scfile.content.models import transforms as T
from scfile.options import Options
from tools.cmd.audit import mappings
from tools.cmd.audit.runner import Case, Plan, PlanError, Suite, Warning
from tools.cmd.audit.schemas import Body, Record


KIND = "body"
NAME = "mcal+mcsb (body)"

OPTIONS = Options(skeleton=True, animation=True, preserve_clips=True)


def resolve(root: Path, animation: Path, linked: dict[str, list[str]]) -> tuple[str | None, list[str]]:
    relative = animation.relative_to(root)
    for path in (relative, *relative.parents):
        key = path.as_posix().casefold()
        if key in linked:
            return key, linked[key]
    return None, []


def validate(root: Path, animation: Path, model: Path) -> list[Record]:
    with formats.McalDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    with formats.McsbDecoder(model, OPTIONS) as decoder:
        target = decoder.decode()

    scene = T.apply_skeletal_animation(source.scene, target.scene)
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
    value = mappings.read(KIND)
    linked = {path.casefold(): models for path, models in mappings.animations(KIND).items()}
    excluded = {item["animation"].casefold() for item in value.get("excluded", [])}
    used: set[str] = set()

    for animation in animations:
        if animation.relative_to(root).as_posix().casefold() in excluded:
            continue

        key, model_paths = resolve(root, animation, linked)
        if key is None:
            warnings.append(Warning(KIND, {"animation": animation}, "No body model match."))
            continue
        used.add(key)

        for relative in model_paths:
            model = root / relative
            if not model.is_file():
                warnings.append(Warning(KIND, {"animation": animation, "model": model}, "Mapped model does not exist."))
                continue

            cases.append(
                Case(
                    {"animation": animation, "model": model},
                    partial(validate, root, animation, model),
                    files=2,
                )
            )

    warnings.extend(
        Warning(KIND, {"animation": root / path}, "Mapped animation path does not exist.")
        for path in linked.keys() - used
    )

    return Plan([Suite(KIND, NAME, cases)], warnings)
