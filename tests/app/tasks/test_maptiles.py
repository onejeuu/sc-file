from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskItem, TaskProgress, TaskStarted
from scfile.app.tasks import TaskContext, execute
from scfile.app.tasks.maptiles import MapTilesImage, MapTilesTask
from scfile.convert import maptiles
from scfile.options import Options


def test_merge(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "map.jpg"
    tiles = {maptiles.Region(0, 0): tmp_path / "r.0.0.ol"}
    save = {"format": "JPEG", "quality": 80}
    task = MapTilesTask(tiles, output, Options(), save)
    calls = []

    def render(*args, **kwargs):
        calls.append((args, kwargs))
        for path in tiles.values():
            kwargs["progress"](path)
        return maptiles.AssembleResult(output, 3)

    monkeypatch.setattr(maptiles, "render", render)

    events = []
    summary = execute(task, events.append)

    assert calls[0][1]["save"] == save
    assert isinstance(events[0], TaskStarted)
    assert events[0].total == 2
    assert isinstance(events[1], TaskProgress)
    assert events[1].source == str(next(iter(tiles.values())))
    assert isinstance(events[2], TaskItem)
    assert events[2].output == output
    assert events[2].detail == "Assembled 3 tiles"
    assert summary.work.completed == 1
    assert summary.files.written == 1


def test_cancelled(tmp_path: Path, monkeypatch) -> None:
    tiles = {maptiles.Region(0, 0): tmp_path / "r.0.0.ol"}
    task = MapTilesTask(tiles, tmp_path / "map.jpg", Options(), {"format": "JPEG"})

    def interrupted(*args, **kwargs):
        raise exceptions.MergeInterrupted()

    monkeypatch.setattr(maptiles, "render", interrupted)

    assert len(list(task.run(TaskContext()))) == 1


def test_image_size_estimate() -> None:
    assert MapTilesImage.JPEG.estimate(1_000, 92) == (100, 180)
    assert MapTilesImage.PNG.estimate(1_000, 0) == (3_000, 3_000)
    assert MapTilesImage.PNG.estimate(1_000, 6) == (483, 959)
