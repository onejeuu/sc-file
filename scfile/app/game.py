from __future__ import annotations

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
    root: Path

    @classmethod
    def from_root(cls, path: Path) -> Installation | None:
        return cls(path.resolve()) if is_root(path) else None

    @property
    def assets(self) -> Path:
        return self.root / ASSETS

    @property
    def map_cache(self) -> Path:
        return self.root / MAP_CACHE


def is_root(path: Path) -> bool:
    return path.is_dir() and ((path / ASSETS).is_dir() or (path / MAP_CACHE).is_dir())


def is_map_cache(path: Path) -> bool:
    return path.is_dir() and any(path.glob("*/*.mdat"))


def is_minecraft_world(path: Path) -> bool:
    return (path / "level.dat").is_file()


def resolve_minecraft_regions(path: Path) -> Path:
    if path.name == "region" and is_minecraft_world(path.parent):
        return path

    if is_minecraft_world(path):
        return path / "region"

    return path


def resolve(path: Path) -> Installation | None:
    visited: set[Path] = set()
    for candidate in _candidates(path.expanduser()):
        if candidate in visited:
            continue
        visited.add(candidate)

        if installation := Installation.from_root(candidate):
            return installation

    return None


def resolve_map_cache(path: Path) -> Path:
    if is_map_cache(path):
        return path

    installation = resolve(path)
    if installation and is_map_cache(installation.map_cache):
        return installation.map_cache

    return path


def _suffixes(path: Path) -> Iterator[Path]:
    for index in range(len(path.parts)):
        yield Path(*path.parts[index:])


def _candidates(path: Path) -> Iterator[Path]:
    source = path if path.is_dir() else path.parent
    yield source
    yield from source.parents

    # Complete known layouts only below the path selected by the user
    suffixes = tuple(suffix for pattern in _ROOT_PATTERNS for suffix in _suffixes(pattern))
    for suffix in suffixes:
        yield source / suffix
