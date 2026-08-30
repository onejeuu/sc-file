from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskItem, TaskProgress, TaskStarted
from scfile.app.tasks import TaskContext, execute
from scfile.app.tasks.mapmerge import MapImageFormat, MapMergeTask
from scfile.convert import mapmerge
from scfile.options import Options


def test_merge(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "map.jpg"
    tiles = {mapmerge.Region(0, 0): tmp_path / "r.0.0.ol"}
    save = {"format": "JPEG", "quality": 80}
    task = MapMergeTask(tiles, output, Options(), save)
    calls = []

    def render(*args, **kwargs):
        calls.append((args, kwargs))
        for path in tiles.values():
            kwargs["progress"](path)
        return mapmerge.MergeResult(output, 3)

    monkeypatch.setattr(mapmerge, "render", render)

    events = []
    summary = execute(task, events.append)

    assert calls[0][1]["save"] == save
    assert isinstance(events[0], TaskStarted)
    assert events[0].total == 2
    assert isinstance(events[1], TaskProgress)
    assert events[1].source == str(next(iter(tiles.values())))
    assert isinstance(events[2], TaskItem)
    assert events[2].output == output
    assert events[2].detail == "Merged 3 tiles"
    assert summary.work.completed == 1
    assert summary.files.written == 1


def test_cancelled(tmp_path: Path, monkeypatch) -> None:
    tiles = {mapmerge.Region(0, 0): tmp_path / "r.0.0.ol"}
    task = MapMergeTask(tiles, tmp_path / "map.jpg", Options(), {"format": "JPEG"})

    def interrupted(*args, **kwargs):
        raise exceptions.MergeInterrupted()

    monkeypatch.setattr(mapmerge, "render", interrupted)

    assert len(list(task.run(TaskContext()))) == 1


def test_image_size_estimate() -> None:
    assert MapImageFormat.JPEG.estimate(1_000, 92) == (100, 180)
    assert MapImageFormat.PNG.estimate(1_000, 0) == (3_000, 3_000)
    assert MapImageFormat.PNG.estimate(1_000, 6) == (483, 959)
