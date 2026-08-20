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


@dataclass(frozen=True, slots=True)
class MinecraftWorld:
    root: Path
    regions: Path

    def is_valid(self) -> bool:
        return is_minecraft_world(self.root) and self.regions.name == "region"


def is_root(path: Path) -> bool:
    return path.is_dir() and ((path / ASSETS).is_dir() or (path / MAP_CACHE).is_dir())


def is_minecraft_world(path: Path) -> bool:
    return (path / "level.dat").is_file()


def resolve_minecraft_world(path: Path) -> MinecraftWorld | None:
    path = path.resolve()

    for candidate in (path, *path.parents):
        if not is_minecraft_world(candidate):
            continue

        regions = candidate / "region"
        if not regions.is_dir():
            regions = candidate / "dimensions/minecraft/overworld/region"

        return MinecraftWorld(candidate, regions) if regions.is_dir() else None

    return None


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
    path = path.resolve()
    installation = resolve(path)

    if not installation:
        return path

    if installation.map_cache in path.parents or path == installation.map_cache:
        return path

    return installation.map_cache


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
