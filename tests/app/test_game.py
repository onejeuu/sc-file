from pathlib import Path

import pytest

from scfile.app.game import ASSETS, MAP_CACHE, GameRoot, McWorld


@pytest.fixture
def world_path(tmp_path: Path, regions_path: str) -> Path:
    world = tmp_path / "world"
    world.mkdir()
    (world / "level.dat").touch()

    regions = world / regions_path
    regions.mkdir(parents=True)

    return world


def test_game_root(tmp_path: Path) -> None:
    root = tmp_path / "game"
    (root / ASSETS).mkdir(parents=True)

    game = GameRoot.find(root / ASSETS)

    assert game is not None
    assert game.root == root.resolve()
    assert game.assets == root.resolve() / ASSETS

    assert GameRoot.from_path(root) == game
    assert GameRoot.from_path(root / ASSETS) is None


def test_asset(tmp_path: Path) -> None:
    root = tmp_path / "game"
    source = root / ASSETS / "highpoly/animations/wpn_fp_test.mcvd"
    source.parent.mkdir(parents=True)
    source.touch()

    game = GameRoot.from_path(root)
    assert game is not None

    for value in (
        "modassets/assets/highpoly/animations/wpn_fp_test.mcvd",
        "assets/highpoly/animations/wpn_fp_test.mcvd",
        "highpoly/animations/wpn_fp_test.mcvd",
    ):
        assert game.resolve_asset(value) == source.resolve()

    assert game.resolve_asset(source) is None
    assert game.resolve_asset("assets/../outside.mcvd") is None


def test_map_cache(tmp_path: Path) -> None:
    cache = tmp_path / MAP_CACHE
    region = cache / "world"
    region.mkdir(parents=True)
    (region / "r.0.0.mdat").write_bytes(b"data")

    game = GameRoot.from_path(tmp_path)
    assert game is not None
    assert game.resolve_map_cache(tmp_path) == cache.resolve()


@pytest.mark.parametrize("regions_path", ["region", "dimensions/minecraft/overworld/region"])
def test_world(world_path: Path, regions_path: str) -> None:
    world = McWorld.find(world_path)

    assert world is not None
    assert world.root == world_path.resolve()
    assert world.regions == (world_path / regions_path).resolve()
    assert world.is_valid()


def test_unrelated(tmp_path: Path) -> None:
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()

    assert GameRoot.find(unrelated) is None
    assert McWorld.find(unrelated) is None


def test_nested_game_path(tmp_path: Path) -> None:
    root = tmp_path / "game"
    assets = root / ASSETS
    cache = root / MAP_CACHE
    assets.mkdir(parents=True)
    cache.mkdir(parents=True)

    nested = cache / "nested"
    nested.mkdir()

    game = GameRoot.find(assets / "nested")
    assert game is not None
    assert game == GameRoot(root.resolve())
    assert game.resolve_map_cache(nested) == nested.resolve()
