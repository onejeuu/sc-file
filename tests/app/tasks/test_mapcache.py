from pathlib import Path

from scfile.app.events import TaskError
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
