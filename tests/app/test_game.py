from pathlib import Path

import pytest

from scfile.app import game


@pytest.fixture
def mcworld_path(tmp_path: Path, regions_path: str) -> Path:
    world = tmp_path / "world"
    world.mkdir()
    (world / "level.dat").touch()

    regions = world / regions_path
    regions.mkdir(parents=True)

    return world


def test_installation(tmp_path: Path) -> None:
    root = tmp_path / "stalcraft"
    (root / game.ASSETS).mkdir(parents=True)

    installation = game.resolve(root / game.ASSETS)

    assert installation is not None
    assert installation.root == root.resolve()
    assert installation.assets == root.resolve() / game.ASSETS

    assert game.Installation.from_root(root) == installation
    assert game.Installation.from_root(root / game.ASSETS) is None


def test_map_cache(tmp_path: Path) -> None:
    cache = tmp_path / game.MAP_CACHE
    region = cache / "world"
    region.mkdir(parents=True)
    (region / "r.0.0.mdat").write_bytes(b"data")

    assert game.resolve_map_cache(tmp_path) == cache.resolve()


@pytest.mark.parametrize("regions_path", ["region", "dimensions/minecraft/overworld/region"])
def test_minecraft(mcworld_path: Path, regions_path: str) -> None:
    mcworld = game.resolve_minecraft_world(mcworld_path)

    assert game.is_minecraft_world(mcworld_path)
    assert mcworld is not None
    assert mcworld.root == mcworld_path.resolve()
    assert mcworld.regions == (mcworld_path / regions_path).resolve()
    assert mcworld.is_valid()


def test_unrelated(tmp_path: Path) -> None:
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()

    assert game.resolve(unrelated) is None
    assert game.resolve_map_cache(unrelated) == unrelated
    assert not game.is_minecraft_world(unrelated)
    assert game.resolve_minecraft_world(unrelated) is None


def test_nested(tmp_path: Path) -> None:
    root = tmp_path / "stalcraft"
    assets = root / game.ASSETS
    cache = root / game.MAP_CACHE
    assets.mkdir(parents=True)
    cache.mkdir(parents=True)

    nested = cache / "nested"
    nested.mkdir()

    assert game.resolve(assets / "nested") == game.Installation(root.resolve())
    assert game.resolve_map_cache(nested) == nested.resolve()
