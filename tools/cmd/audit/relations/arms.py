from functools import partial
from pathlib import Path

from scfile import formats
from scfile.options import Options
from scfile.structures.models import transforms as T
from tools.cmd.audit import mappings
from tools.cmd.audit.runner import Case, Plan, PlanError, Suite, Warning
from tools.cmd.audit.schemas import Arms, Record


KIND = "arms"
NAME = "mcvd+mcsb (arms)"

ANIMATIONS = Path("highpoly/animations")
HANDS = Path("highpoly/character_hands.mcsb")

OPTIONS = Options(skeleton=True, animation=True)


def validate(root: Path, animation: Path, weapon: Path | None, hands: Path) -> list[Record]:
    with formats.McvdDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    contents = []
    for path in filter(None, (weapon, hands)):
        with formats.McsbDecoder(path, OPTIONS) as decoder:
            contents.append(decoder.decode())

    scene = T.apply_fp_models(source.scene, *(model.scene for model in contents))
    clips = source.scene.animation.clips
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
