from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskItem, TaskProgress, TaskStarted
from scfile.app.tasks import TaskContext, execute
from scfile.app.tasks.maptiles import MapTilesImage, MapTilesTask
from scfile.convert import maptiles
from scfile.options import Options


def test_run(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "map.jpg"
    tile = tmp_path / "r.0.0.ol"
    tiles = {maptiles.Region(0, 0): tile}
    save = {"format": "JPEG", "quality": 80}
    task = MapTilesTask(tiles, output, Options(), save)
    received = {}

    def render(actual, target, **options):
        assert actual == tiles
        assert target == output
        received.update(options)
        options["progress"](tile)
        return maptiles.AssembleResult(output, 3)

    monkeypatch.setattr(maptiles, "render", render)

    events = []
    summary = execute(task, events.append)

    assert received["save"] == save
    assert [type(event) for event in events] == [TaskStarted, TaskProgress, TaskItem]
    assert events[0].total == len(tiles) + 1
    assert events[1].source == str(tile)
    assert events[2].output == output
    assert summary.files.written == 1


def test_cancelled(tmp_path: Path, monkeypatch) -> None:
    tiles = {maptiles.Region(0, 0): tmp_path / "r.0.0.ol"}
    task = MapTilesTask(tiles, tmp_path / "map.jpg", Options(), {"format": "JPEG"})

    def interrupted(*args, **kwargs):
        raise exceptions.MergeInterrupted()

    monkeypatch.setattr(maptiles, "render", interrupted)

    events = list(task.run(TaskContext()))

    assert len(events) == 1
    assert isinstance(events[0], TaskStarted)


def test_estimate() -> None:
    pixels = 1_000
    jpeg = (MapTilesImage.JPEG.estimate(pixels, value) for value in (80, 95))
    png = (MapTilesImage.PNG.estimate(pixels, value) for value in (0, 6))
    jpeg_low, jpeg_high = jpeg
    png_raw, png_compressed = png

    assert jpeg_low[0] < jpeg_high[0]
    assert jpeg_low[1] < jpeg_high[1]
    assert png_raw == (pixels * 3, pixels * 3)
    assert png_compressed[0] <= png_compressed[1] < png_raw[0]
