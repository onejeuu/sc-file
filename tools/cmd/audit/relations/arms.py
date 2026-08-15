from collections import defaultdict
from functools import partial
from pathlib import Path

from scfile import formats
from scfile.options import Options
from scfile.structures.models import transforms
from tools.cmd.audit import rules
from tools.cmd.audit.runner import Case, Plan, PlanError, Suite, Warning
from tools.cmd.audit.schemas import Arms, Record


KIND = "arms"
NAME = "mcvd+mcsb (arms)"

ANIMATIONS = Path("highpoly/animations")
MODELS = Path("weapons/models")
HANDS = Path("highpoly/character_hands.mcsb")
SUBTYPES = ("weapons", "meleeweapons")
WEAPON_FP_PREFIX = "wpn_fp_"

OPTIONS = Options(model=Options.Model(skeleton=True, animation=True))


def weapon_name(path: Path) -> str:
    return path.stem.casefold().removeprefix(WEAPON_FP_PREFIX)


def models(root: Path) -> dict[str, list[Path]]:
    indexed: defaultdict[str, list[Path]] = defaultdict(list)
    for subtype in SUBTYPES:
        for path in sorted((root / MODELS / subtype).rglob("*.mcsb")):
            indexed[weapon_name(path)].append(path)
    return dict(indexed)


def resolve(
    root: Path,
    animation: Path,
    indexed: dict[str, list[Path]],
) -> tuple[list[Path], list[Warning]]:
    mapped = rules.ARMS_MODELS.get(animation.name)
    if mapped is None:
        matched = indexed.get(weapon_name(animation), []).copy()
        mapped = ()
    else:
        matched = []
    warnings = []

    for linked in mapped:
        model = root / MODELS / linked
        if not model.is_file():
            warnings.append(Warning(KIND, {"animation": animation}, f"Linked model does not exist: {linked}"))
            continue
        if model not in matched:
            matched.append(model)

    if not matched:
        warnings.append(Warning(KIND, {"animation": animation}, "No weapon model match."))

    return matched, warnings


def validate(root: Path, animation: Path, weapon: Path | None, hands: Path) -> list["Record"]:
    with formats.McvdDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    contents = []
    for path in (weapon, hands):
        if path is None:
            continue
        with formats.McsbDecoder(path, OPTIONS) as decoder:
            contents.append(decoder.decode())

    scene = transforms.apply_fp_models(source.scene, *(model.scene for model in contents))
    clips = source.scene.animation.clips
    record = Arms(
        animation=animation.relative_to(root).as_posix(),
        model=weapon.relative_to(root).as_posix() if weapon is not None else "",
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

    warnings = []
    cases = []

    hands_only = [animation for animation in animations if animation.name in rules.ARMS_HANDS_ONLY]
    for animation in hands_only:
        cases.append(
            Case(
                {"animation": animation, "hands": hands},
                partial(validate, root, animation, None, hands),
                files=2,
            )
        )

    indexed = models(root)
    for animation in (animation for animation in animations if animation.name not in rules.ARMS_HANDS_ONLY):
        matched, issues = resolve(root, animation, indexed)
        warnings.extend(issues)

        for model in matched:
            cases.append(
                Case(
                    {"animation": animation, "model": model, "hands": hands},
                    partial(validate, root, animation, model, hands),
                    files=2,
                )
            )

    suite = Suite(KIND, NAME, cases)
    return Plan([suite], warnings)
