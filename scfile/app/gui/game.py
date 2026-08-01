"""STALCRAFT installation path resolution."""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


ASSETS = Path("modassets/assets")
MAP_CACHE = Path("map_cache/5.0")

_ROOT_PATTERNS = (
    Path("EXBO/runtime/stalcraft"),
    Path("steamapps/common/STALCRAFT"),
    Path("AppData/Roaming/EXBO/runtime/stalcraft"),
)


@dataclass(frozen=True, slots=True)
class Installation:
    """Resolved game installation and its data locations."""

    root: Path

    @property
    def assets(self) -> Path:
        return self.root / ASSETS

    @property
    def map_cache(self) -> Path:
        return self.root / MAP_CACHE


def is_root(path: Path) -> bool:
    """Return whether a directory contains known game data."""

    return path.is_dir() and ((path / ASSETS).is_dir() or (path / MAP_CACHE).is_dir())


def is_map_cache(path: Path) -> bool:
    """Return whether a directory contains map cache regions."""

    return path.is_dir() and any(path.glob("*/*.mdat"))


def _suffixes(path: Path) -> Iterator[Path]:
    for index in range(len(path.parts)):
        yield Path(*path.parts[index:])


def _candidates(path: Path) -> Iterator[Path]:
    source = path if path.is_dir() else path.parent
    bases = (source, *source.parents)
    yield from bases

    suffixes = tuple(suffix for pattern in _ROOT_PATTERNS for suffix in _suffixes(pattern))
    for base in bases:
        for suffix in suffixes:
            yield base / suffix


def resolve(path: Path) -> Installation | None:
    """Resolve any nearby path to a game installation root."""

    visited: set[Path] = set()
    for candidate in _candidates(path.expanduser()):
        if candidate in visited:
            continue
        visited.add(candidate)

        if is_root(candidate):
            return Installation(candidate.resolve())

    return None


def resolve_map_cache(path: Path) -> Path:
    """Resolve any nearby path to a populated map cache directory."""

    if is_map_cache(path):
        return path

    installation = resolve(path)
    if installation and is_map_cache(installation.map_cache):
        return installation.map_cache

    return path
