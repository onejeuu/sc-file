from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskItem
from scfile.app.tasks import TaskContext
from scfile.app.tasks.mapmerge import MapMergeTask
from scfile.convert import mapmerge
from scfile.options import Options


def test_merge(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "map.jpg"
    task = MapMergeTask(tmp_path, output, Options())
    monkeypatch.setattr(mapmerge, "merge", lambda *args: mapmerge.MergeResult(output, 3))

    events = list(task.run(TaskContext()))

    assert isinstance(events[1], TaskItem)
    assert events[1].output == output
    assert events[1].detail == "Merged 3 tiles"


def test_cancelled(tmp_path: Path, monkeypatch) -> None:
    task = MapMergeTask(tmp_path, tmp_path / "map.jpg", Options())

    def interrupted(*args):
        raise exceptions.MergeInterrupted()

    monkeypatch.setattr(mapmerge, "merge", interrupted)

    assert len(list(task.run(TaskContext()))) == 1
