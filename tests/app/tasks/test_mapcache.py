from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskError, TaskItemFailure
from scfile.app.tasks import TaskContext, execute
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.convert import mapcache
from scfile.options import Options


def test_missing(tmp_path: Path) -> None:
    events = []

    summary = execute(MapCacheTask(tmp_path / "missing", None, Options(), workers=1), events.append)

    error = events[1]
    assert isinstance(error, TaskError)
    assert isinstance(error.error, FileNotFoundError)
    assert error.traceback is None
    assert summary.work.failed == 1


def test_empty(tmp_path: Path) -> None:
    events = []

    execute(MapCacheTask(tmp_path, None, Options(), workers=1), events.append)

    assert isinstance(events[1], TaskError)
    assert isinstance(events[1].error, exceptions.RegionError)


def test_invalid(tmp_path: Path) -> None:
    (tmp_path / "invalid.mdat").write_bytes(b"data")
    events = []

    execute(MapCacheTask(tmp_path, None, Options(), workers=1), events.append)

    assert isinstance(events[1], TaskError)
    assert isinstance(events[1].error, exceptions.RegionError)


def test_merge_error(tmp_path: Path, monkeypatch) -> None:
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


def test_merge_errors(tmp_path: Path, monkeypatch) -> None:
    task = MapCacheTask(tmp_path, None, Options())
    region = ((0, 0), [tmp_path / "r.0.0.mdat"])
    context = TaskContext()

    monkeypatch.setattr(
        "scfile.app.tasks.mapcache.mapcache.merge",
        lambda *args, **kwargs: (_ for _ in ()).throw(exceptions.MergeInterrupted()),
    )
    assert task._merge(region, context) is None

    expected = exceptions.RegionError("broken", location="source")
    monkeypatch.setattr(
        "scfile.app.tasks.mapcache.mapcache.merge",
        lambda *args, **kwargs: (_ for _ in ()).throw(expected),
    )
    failure = task._merge(region, context)
    assert isinstance(failure, TaskItemFailure)
    assert failure.source == "source"

    monkeypatch.setattr(
        "scfile.app.tasks.mapcache.mapcache.merge",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError()),
    )
    failure = task._merge(region, context)
    assert isinstance(failure, TaskItemFailure)
    assert failure.traceback is not None


def test_scan_error(tmp_path: Path, monkeypatch) -> None:
    error = OSError(13, "denied", str(tmp_path))
    monkeypatch.setattr(mapcache, "scan", lambda *args: mapcache.ScanResult([], [error]))

    events = list(MapCacheTask(tmp_path, None, Options()).run(TaskContext()))

    assert isinstance(events[1], TaskError)
    assert events[1].source == str(tmp_path)
