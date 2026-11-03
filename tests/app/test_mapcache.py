from pathlib import Path

from scfile.app.mapcache import options_for_path, supported_version_from_path, version_from_path
from scfile.options import Options


def test_version_from_path() -> None:
    assert version_from_path(Path("game/map_cache/6.1")) == 6
    assert supported_version_from_path(Path("game/map_cache/6.1")) == 6
    assert supported_version_from_path(Path("game/map_cache/8.0")) is None


def test_options_for_path_keeps_explicit_version() -> None:
    assert options_for_path(Options(), Path("game/map_cache/5.0")).mdat_version == 5
    assert options_for_path(Options(mdat_version=7), Path("game/map_cache/5.0")).mdat_version == 7
