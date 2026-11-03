import re
from dataclasses import replace
from pathlib import Path

from scfile.formats.mdat.versions import SUPPORTED_VERSIONS
from scfile.options import MdatVersion, Options


_VERSION_PATH = re.compile(r"^(?P<major>\d+)\.\d+$")


def version_from_path(path: Path) -> int | None:
    """Return the MDAT major version encoded by a map cache path."""

    for parent in path.parents:
        if parent.name.lower() != "map_cache":
            continue

        match = _VERSION_PATH.fullmatch(path.relative_to(parent).parts[0])
        if match:
            return int(match.group("major"))

    return None


def supported_version_from_path(path: Path) -> MdatVersion | None:
    version = version_from_path(path)
    return version if version in SUPPORTED_VERSIONS else None


def options_for_path(options: Options, path: Path) -> Options:
    """Apply path-based MDAT detection without overriding an explicit choice."""

    if options.mdat_version is not None:
        return options

    version = supported_version_from_path(path)
    if version is None:
        return options

    return replace(options, mdat_version=version)
