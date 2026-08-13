from pathlib import Path

from scfile.app import game


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


def test_minecraft(tmp_path: Path) -> None:
    world = tmp_path / "world"
    world.mkdir()
    (world / "level.dat").touch()

    regions = world / "region"
    assert game.is_minecraft_world(world)
    assert game.resolve_minecraft_regions(world) == regions
    assert game.resolve_minecraft_regions(regions) == regions


def test_unrelated(tmp_path: Path) -> None:
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()

    assert game.resolve(unrelated) is None
    assert game.resolve_map_cache(unrelated) == unrelated
    assert not game.is_minecraft_world(unrelated)
    assert game.resolve_minecraft_regions(unrelated) == unrelated


def test_nested(tmp_path: Path) -> None:
    root = tmp_path / "stalcraft"
    assets = root / game.ASSETS
    cache = root / game.MAP_CACHE
    assets.mkdir(parents=True)
    cache.mkdir(parents=True)

    assert game.resolve(assets / "nested") == game.Installation(root.resolve())
    assert game.resolve_map_cache(cache / "nested") == cache.resolve()
