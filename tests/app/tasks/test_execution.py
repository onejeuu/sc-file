from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

from scfile.app.enums import OutputLayout, TaskKind, TaskOutcome
from scfile.app.tasks import (
    Task,
    TaskContext,
    TaskError,
    TaskEvent,
    TaskFailure,
    TaskItem,
    TaskStarted,
    execute,
)
from scfile.app.tasks.convert import ConvertTask
from scfile.options import Options


class SampleTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        output = Path("output")
        yield TaskStarted(self.kind, 3, output)
        yield TaskItem("written", output / "written.obj")
        yield TaskItem("skipped")
        yield TaskFailure("broken", ValueError("broken"))


class BrokenTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.ANIMATE

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, 1)
        raise RuntimeError("broken")


def test_execute_collects_events() -> None:
    events: list[TaskEvent] = []

    summary = execute(SampleTask(), events.append)

    assert isinstance(events[0], TaskStarted)
    assert summary.total == 3
    assert summary.work.completed == 3
    assert summary.work.failed == 1
    assert summary.files.written == 1
    assert summary.files.skipped == 1
    assert summary.output == Path("output")
    assert summary.outcome is TaskOutcome.PARTIAL


def test_execute_reports_unexpected_error() -> None:
    events: list[TaskEvent] = []

    summary = execute(BrokenTask(), events.append)

    assert isinstance(events[-1], TaskError)
    assert summary.work.completed == 0
    assert summary.work.failed == 1
    assert summary.outcome is TaskOutcome.FAILED


def test_context_stops_task() -> None:
    context = TaskContext()
    context.stop()

    assert context.stopped


def test_convert_task(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    events: list[TaskEvent] = []
    task = ConvertTask((source,), (), Options(), output=tmp_path, workers=1)

    summary = execute(task, events.append)

    assert isinstance(events[0], TaskStarted)
    assert events[0].total == 1
    assert summary.work.completed == 1
    assert summary.files.written == 1
    assert (tmp_path / "document.json").exists()


def test_relative_layout(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    root = tmp_path / "assets"
    nested = root / "documents"
    nested.mkdir(parents=True)
    document = nested / source.name
    document.write_bytes(source.read_bytes())

    task = ConvertTask((root,), (), Options(), output=tmp_path / "output", layout=OutputLayout.RELATIVE, workers=1)
    execute(task)

    assert (tmp_path / "output/documents/document.json").exists()


def test_rooted_layout(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    root = tmp_path / "assets"
    nested = root / "documents"
    nested.mkdir(parents=True)
    document = nested / source.name
    document.write_bytes(source.read_bytes())

    task = ConvertTask((root,), (), Options(), output=tmp_path / "output", layout=OutputLayout.ROOTED, workers=1)
    execute(task)

    assert (tmp_path / "output/assets/documents/document.json").exists()
