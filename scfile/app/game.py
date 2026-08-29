from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ASSETS: Path = Path("modassets/assets")
MAP_CACHE: Path = Path("map_cache/5.0")
LOCALIZED: Path = Path("_localized")
PATCHASSETS: Path = Path("patchassets/assets")

GAME_ROOTS: tuple[Path, ...] = (
    Path("EXBO/runtime/stalcraft"),
    Path("steamapps/common/STALCRAFT"),
    Path("AppData/Roaming/EXBO/runtime/stalcraft"),
)

type Realm = Literal["ru", "global"]


class GameRegion(str):
    @property
    def realm(self) -> Realm:
        match self:
            case "ru":
                return "ru"
            case _:
                return "global"


@dataclass(frozen=True, slots=True)
class GameRoot:
    root: Path

    @classmethod
    def from_path(cls, path: Path) -> GameRoot | None:
        root = path.resolve()
        if root.is_dir() and ((root / ASSETS).is_dir() or (root / MAP_CACHE).is_dir()):
            return cls(root)

        return None

    @classmethod
    def find(cls, path: Path) -> GameRoot | None:
        visited: set[Path] = set()
        for candidate in _game_candidates(path.expanduser()):
            if candidate in visited:
                continue
            visited.add(candidate)

            if root := cls.from_path(candidate):
                return root

        return None

    @property
    def assets(self) -> Path:
        return self.root / ASSETS

    @property
    def map_cache(self) -> Path:
        return self.root / MAP_CACHE

    @property
    def regions(self) -> tuple[GameRegion, ...]:
        localized = self.assets / LOCALIZED
        try:
            return tuple(sorted(GameRegion(path.name) for path in localized.iterdir() if path.is_dir()))

        except OSError:
            return ()

    def asset_layers(self, region: GameRegion) -> tuple[Path, ...]:
        patch = self.root / f"bin_{region.realm}" / PATCHASSETS
        paths = (
            self.assets,
            self.assets / LOCALIZED / region,
            patch,
            patch / LOCALIZED / region,
        )
        return tuple(path for path in paths if path.is_dir())

    def asset_paths(self, relative: str | Path, region: GameRegion) -> tuple[Path, ...]:
        relative = Path(relative)
        if relative.anchor or ".." in relative.parts:
            return ()

        return tuple(path for layer in self.asset_layers(region) if (path := layer / relative).exists())

    def resolve_asset(self, value: str | Path) -> Path | None:
        value = str(value).replace("\\", "/")
        relative = Path(value.removeprefix("modassets/assets/").removeprefix("assets/"))
        if relative.anchor:
            return None

        assets = self.assets.resolve()
        candidate = (assets / relative).resolve()
        if candidate.is_relative_to(assets) and candidate.is_file():
            return candidate

        return None

    def resolve_map_cache(self, path: Path) -> Path:
        path = path.resolve()
        return path if self.map_cache in path.parents or path == self.map_cache else self.map_cache


@dataclass(frozen=True, slots=True)
class McWorld:
    root: Path
    regions: Path

    @classmethod
    def find(cls, path: Path) -> McWorld | None:
        path = path.resolve()

        for candidate in (path, *path.parents):
            if not (candidate / "level.dat").is_file():
                continue

            regions = candidate / "region"
            if not regions.is_dir():
                regions = candidate / "dimensions/minecraft/overworld/region"

            return cls(candidate, regions) if regions.is_dir() else None

        return None

    def is_valid(self) -> bool:
        return (self.root / "level.dat").is_file() and self.regions.is_dir() and self.regions.name == "region"


def _suffixes(path: Path) -> Iterator[Path]:
    for index in range(len(path.parts)):
        yield Path(*path.parts[index:])


def _game_candidates(path: Path) -> Iterator[Path]:
    source = path if path.is_dir() else path.parent
    yield source
    yield from source.parents

    # Complete known layouts only below the path selected by the user
    suffixes = tuple(suffix for pattern in GAME_ROOTS for suffix in _suffixes(pattern))
    for suffix in suffixes:
        yield source / suffix
