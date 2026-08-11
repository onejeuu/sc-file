from pathlib import Path

from scfile.app.enums import AnimateCommand, CliCommand
from scfile.enums import FileFormat
from scfile.registry import RESOLVER


ROOT_OPTIONS = frozenset(("--help", "--version", "--updates"))


def resolve(
    args: list[str],
) -> list[str]:
    if ROOT_OPTIONS.intersection(args) or args[0] in CliCommand:
        return args

    return [*_default_command(args), *args]


def _default_command(
    args: list[str],
) -> list[str]:
    if "map_cache" in args[0]:
        return [str(CliCommand.MAPCACHE)]

    paths = tuple(Path(arg) for arg in args)
    sources = tuple(path for path in paths if RESOLVER.resolve(path) is not None)
    if _is_arms_sources(sources):
        return [str(CliCommand.ANIMATE), str(AnimateCommand.ARMS)]

    return [str(CliCommand.CONVERT)]


def _is_arms_sources(sources: tuple[Path, ...]) -> bool:
    if len(sources) not in (2, 3):
        return False

    animation, *models = sources
    name = animation.stem.lower()
    return (
        animation.suffix.lower() == FileFormat.MCVD.suffix
        and all(model.suffix.lower() == FileFormat.MCSB.suffix for model in models)
        and ("fp_" in name or "wpn_" in name)
    )
