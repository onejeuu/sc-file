from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskError, TaskItemFailure
from scfile.app.tasks import execute
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.options import Options


def test_missing_source_is_task_error(tmp_path: Path) -> None:
    events = []

    summary = execute(MapCacheTask(tmp_path / "missing", None, Options(), workers=1), events.append)

    error = events[1]
    assert isinstance(error, TaskError)
    assert isinstance(error.error, FileNotFoundError)
    assert error.traceback is None
    assert summary.work.failed == 1


def test_empty_source_is_region_error(tmp_path: Path) -> None:
    events = []

    execute(MapCacheTask(tmp_path, None, Options(), workers=1), events.append)

    assert isinstance(events[1], TaskError)
    assert isinstance(events[1].error, exceptions.RegionError)


def test_invalid_region_names_are_task_error(tmp_path: Path) -> None:
    (tmp_path / "invalid.mdat").write_bytes(b"data")
    events = []

    execute(MapCacheTask(tmp_path, None, Options(), workers=1), events.append)

    assert isinstance(events[1], TaskError)
    assert isinstance(events[1].error, exceptions.RegionError)


def test_merge_error_is_item_failure(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "r.0.0.mdat"
    source.write_bytes(b"data")
    monkeypatch.setattr(
        "scfile.app.tasks.mapcache.mapcache.merge",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError(5, "denied", str(source))),
    )
    events = []

    summary = execute(MapCacheTask(tmp_path, None, Options(), workers=1), events.append)

    assert isinstance(events[1], TaskItemFailure)
    assert isinstance(events[1].error, OSError)
    assert summary.work.failed == 1
