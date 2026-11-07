import json
import re
from dataclasses import replace
from pathlib import Path

from scfile.exceptions import BlockMappingError
from scfile.formats.mca import mappings
from scfile.formats.mdat.versions import SUPPORTED_VERSIONS
from scfile.options import BlockMapping, MdatVersion, Options


_VERSION_PATH = re.compile(r"^(?P<major>\d+)\.\d+$")


def load_block_mappings(specs: tuple[str, ...]) -> tuple[BlockMapping, ...] | None:
    """Resolve ordered built-in names, JSON files, and inline JSON objects."""

    if not specs:
        return None

    return tuple(_load_block_mapping(spec) for spec in specs)


def _load_block_mapping(spec: str) -> BlockMapping:
    name = spec.casefold()
    if name in mappings.BUILTIN:
        return mappings.BUILTIN[name]

    inline = spec.lstrip().startswith("{")
    if inline:
        source = "inline JSON"
        text = spec
    else:
        path = Path(spec).expanduser()
        source = str(path)
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError as error:
            raise BlockMappingError(f"Cannot read block mapping '{source}': {error}.") from error

    try:
        data = json.loads(text)

    except json.JSONDecodeError as error:
        raise BlockMappingError(
            f"Invalid JSON in block mapping '{source}' at line {error.lineno}, column {error.colno}."
        ) from error

    if not isinstance(data, dict):
        raise BlockMappingError(f"Block mapping '{source}' must contain a JSON object.")

    try:
        mappings.compile(data)

    except BlockMappingError as error:
        raise BlockMappingError(f"Block mapping '{source}': {error}") from error

    return data


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
