from pathlib import Path

from scfile.app.events import TaskError
from scfile.app.tasks import execute
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.convert.mapcache import group, scan
from scfile.options import Options


def test_group() -> None:
    paths = [
        Path("r.0.0.mdat"),
        Path("reg.1.-1.mdat"),
        Path("invalid.mdat"),
    ]

    assert group(paths) == {
        (0, 0): [Path("r.0.0.mdat")],
        (1, -1): [Path("reg.1.-1.mdat")],
    }


def test_scan(tmp_path: Path) -> None:
    (tmp_path / "r.0.0.mdat").write_bytes(b"data")
    (tmp_path / "empty.mdat").write_bytes(b"")
    (tmp_path / "cached.bck.mdat").write_bytes(b"data")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "r.1.0.mdat").write_bytes(b"data")

    result = scan(tmp_path)

    assert {path.name for path in result.paths} == {"r.0.0.mdat", "r.1.0.mdat"}
    assert not result.errors


def test_missing_source_is_task_error(tmp_path: Path) -> None:
    events = []
    summary = execute(MapCacheTask(tmp_path / "missing", None, Options(), workers=1), events.append)

    error = events[1]
    assert isinstance(error, TaskError)
    assert isinstance(error.error, FileNotFoundError)
    assert error.traceback is None
    assert summary.work.failed == 1
