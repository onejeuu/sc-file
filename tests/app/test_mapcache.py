from pathlib import Path
from types import SimpleNamespace

import pytest

from scfile.app.mapcache import options_for_path, supported_version_from_path, version_from_path
from scfile.app.tasks.base import TaskContext
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.convert import mapcache
from scfile.convert.regions import Region
from scfile.core import Resources
from scfile.formats.mca import mappings as mca_mapping
from scfile.options import Options


def test_version_from_path() -> None:
    assert version_from_path(Path("game/map_cache/6.1")) == 6
    assert supported_version_from_path(Path("game/map_cache/6.1")) == 6
    assert supported_version_from_path(Path("game/map_cache/8.0")) is None


def test_options_for_path_keeps_explicit_version() -> None:
    assert options_for_path(Options(), Path("game/map_cache/5.0")).mdat_version == 5
    assert options_for_path(Options(mdat_version=7), Path("game/map_cache/5.0")).mdat_version == 7


def test_mapcache_task_shares_resources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "map_cache"
    source.mkdir()
    first = source / "reg.0.0.mdat"
    second = source / "reg.1.0.mdat"
    first.touch()
    second.touch()

    regions = {Region(0, 0): [first], Region(1, 0): [second]}
    monkeypatch.setattr(mapcache, "scan", lambda *args: SimpleNamespace(paths=[first, second], errors=[]))
    monkeypatch.setattr(mapcache, "group", lambda paths: regions)
    monkeypatch.setattr(
        "scfile.app.tasks.mapcache.parallel", lambda items, operation, context, workers: map(operation, items)
    )

    original = mca_mapping.build
    compiled = []

    def track(mappings=None):
        compiled.append(mappings)
        return original(mappings)

    monkeypatch.setattr(mca_mapping, "build", track)
    received = []

    def merge(key, sources, output, options, cancelled=None, resources=None):
        received.append(resources)
        return (f"r.{key.x}.{key.z}.mca", len(sources))

    monkeypatch.setattr(mapcache, "merge", merge)
    task = MapCacheTask(source=source, output=tmp_path / "out", options=Options(block_mappings={"5": "73"}))
    list(task.run(TaskContext()))

    assert len(compiled) == 1
    assert len(received) == 2
    assert received[0] is received[1]
    assert isinstance(received[0], Resources)
    mapping, byte_mapping = received[0][mca_mapping.RESOURCE_KEY]
    assert mapping.ids[5] == 73
    assert byte_mapping is not None


def test_scan_finds_mdat_files(tmp_path: Path) -> None:
    source = tmp_path / "map_cache"
    source.mkdir()
    region = source / "reg.0.0.mdat"
    region.write_bytes(b"sample")
    (source / "reg.1.0.txt").write_bytes(b"sample")

    result = mapcache.scan(source)

    assert result.paths == [region]
    assert not result.errors
