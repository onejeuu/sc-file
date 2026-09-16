from pathlib import Path

from scfile.app.enums import AnimateCommand, CliCommand


ROOT_OPTIONS = frozenset(("--help", "--version", "--updates"))


def resolve(args: list[str]) -> list[str]:
    if ROOT_OPTIONS.intersection(args) or args[0] in CliCommand:
        return args

    command = _command(tuple(map(Path, args)))
    return [*command, *args]


def _command(paths: tuple[Path, ...]) -> tuple[CliCommand | AnimateCommand, ...]:
    if "map_cache" in paths[0].as_posix():
        return (CliCommand.MAPCACHE,)

    animation = _animation(paths)
    if animation is not None:
        return CliCommand.ANIMATE, animation

    return (CliCommand.CONVERT,)


def _animation(paths: tuple[Path, ...]) -> AnimateCommand | None:
    animations = tuple(path for path in paths if path.suffix.lower() in (".mcal", ".mcvd"))
    models = tuple(path for path in paths if path.suffix.lower() == ".mcsb")
    if len(animations) != 1 or not models:
        return None

    animation = animations[0]

    if animation.suffix.lower() == ".mcal" and len(models) == 1:
        return AnimateCommand.BODY

    if animation.suffix.lower() != ".mcvd":
        return None

    stem = animation.stem.lower()
    weapon_fp = "fp_" in stem or "wpn_" in stem
    if weapon_fp and len(models) in (1, 2):
        return AnimateCommand.ARMS

    if len(models) == 1:
        return AnimateCommand.FACE

    return None
