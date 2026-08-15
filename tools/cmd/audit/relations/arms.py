from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from scfile import formats
from scfile.options import Options
from scfile.structures.models import transforms
from tools.cmd.audit import rules
from tools.cmd.audit.runner import Case, Plan, Suite, Warning


if TYPE_CHECKING:
    from tools.cmd.audit.schemas import Record


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
) -> Path | Warning:
    match rules.ARMS_OVERRIDES.get(animation.name):
        case str(mapped):
            model = root / MODELS / mapped
            if model.is_file():
                return model
            return Warning(KIND, {"animation": animation}, f"Mapped model does not exist: {mapped}")

    candidates = indexed.get(weapon_name(animation), [])
    match candidates:
        case [model]:
            return model
        case []:
            return Warning(KIND, {"animation": animation}, "No exact weapon model match.")
        case _:
            names = ", ".join(path.relative_to(root).as_posix() for path in candidates)
            return Warning(KIND, {"animation": animation}, f"Ambiguous exact weapon model match: {names}")


def validate(animation: Path, model_paths: tuple[Path, ...]) -> list["Record"]:
    with formats.McvdDecoder(animation, OPTIONS) as decoder:
        source = decoder.decode()

    contents = []
    for path in model_paths:
        with formats.McsbDecoder(path, OPTIONS) as decoder:
            contents.append(decoder.decode())

    transforms.apply_fp_models(source.scene, *(model.scene for model in contents))
    return []


def build(root: Path) -> Plan:
    animations = sorted((root / ANIMATIONS).glob("*.mcvd"))
    hands = root / HANDS
    hands = hands if hands.is_file() else None
    warnings = []
    cases = []
    connections = 0

    if hands is None:
        warnings.append(Warning(KIND, {}, f"Shared hands model does not exist: {HANDS.as_posix()}"))

    hands_only = [animation for animation in animations if animation.name in rules.ARMS_HANDS_ONLY]
    if hands is not None:
        for animation in hands_only:
            cases.append(
                Case(
                    {"animation": animation, "hands": hands},
                    partial(validate, animation, (hands,)),
                )
            )
            connections += 1

    indexed = models(root)
    for animation in (animation for animation in animations if animation.name not in rules.ARMS_HANDS_ONLY):
        match resolve(root, animation, indexed):
            case Path() as model:
                cases.append(
                    Case(
                        {"animation": animation, "model": model},
                        partial(validate, animation, (model,)),
                    )
                )
                if hands is not None:
                    cases.append(
                        Case(
                            {"animation": animation, "model": model, "hands": hands},
                            partial(validate, animation, (model, hands)),
                        )
                    )
                connections += 1

            case Warning() as warning:
                warnings.append(warning)

    suite = Suite(KIND, NAME, connections * 2, cases)
    return Plan([suite], warnings)
