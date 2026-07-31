"""
Default command routing.
"""

from pathlib import Path

from scfile.enums import AnimateCommand, CliCommand, FileFormat
from scfile.registry import RESOLVER


def resolve(
    args: list[str],
) -> list[str]:
    """Resolve an omitted CLI command from arguments."""

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
