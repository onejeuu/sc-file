from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.app import files
from scfile.app.enums import OutputLayout, TaskKind, TaskOutcome
from scfile.app.events import TaskError, TaskEvent, TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.tasks import Task, TaskContext, execute
from scfile.app.tasks.convert import ConvertTask, _hashed
from scfile.enums import OnConflict
from scfile.options import Options


class SampleTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        output = Path("output")
        yield TaskStarted(self.kind, 3, output)
        yield TaskItem("written", output / "written.obj")
        yield TaskItem("skipped")
        yield TaskItemFailure("broken", ValueError("broken"))


class BrokenTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.ANIMATE

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, 1)
        raise RuntimeError("broken")


def test_execute() -> None:
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


def test_execute_error() -> None:
    events: list[TaskEvent] = []

    summary = execute(BrokenTask(), events.append)

    assert isinstance(events[-1], TaskError)
    assert summary.work.completed == 0
    assert summary.work.failed == 1
    assert summary.outcome is TaskOutcome.FAILED


def test_context() -> None:
    context = TaskContext()
    context.stop()

    assert context.stopped


def test_cancelled_context() -> None:
    context = TaskContext()
    context.stop()

    summary = execute(SampleTask(), context=context)

    assert summary.cancelled


def test_unknown_event() -> None:
    summary = TaskSummary(TaskKind.CONVERT)
    summary.add(object())  # type: ignore[arg-type]

    assert summary.outcome is TaskOutcome.EMPTY


def test_convert(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    events: list[TaskEvent] = []
    task = ConvertTask((source,), (), Options(), output=tmp_path, workers=1)

    summary = execute(task, events.append)

    assert task.layout is OutputLayout.ROOTED
    assert isinstance(events[0], TaskStarted)
    assert events[0].total == 1
    assert summary.work.completed == 1
    assert summary.files.written == 1
    assert (tmp_path / "document.json").exists()


def test_convert_missing(tmp_path: Path) -> None:
    events: list[TaskEvent] = []
    task = ConvertTask((tmp_path / "missing",), (), Options(), workers=2)

    summary = execute(task, events.append)

    assert isinstance(events[0], TaskStarted)
    assert events[0].total == 0
    assert isinstance(events[1], TaskError)
    assert events[1].source == str((tmp_path / "missing").resolve())
    assert summary.work.failed == 1
    assert summary.outcome is TaskOutcome.FAILED


def test_convert_total(tmp_path: Path) -> None:
    task = ConvertTask((tmp_path / "missing",), (), Options(), total=7, workers=1)

    events = list(task.run(TaskContext()))

    assert isinstance(events[0], TaskStarted)
    assert events[0].total == 7


def test_convert_errors(tmp_path: Path, monkeypatch) -> None:
    entry = files.FileEntry(str(tmp_path), str(tmp_path / "source"))
    task = ConvertTask((), (), Options())
    monkeypatch.setattr("scfile.app.tasks.convert.convert.auto", lambda *args: (_ for _ in ()).throw(exceptions.ConversionError("bad")))
    failure = task._convert((entry, tmp_path / "output"))
    assert isinstance(failure, TaskItemFailure)
    assert failure.traceback is None

    monkeypatch.setattr("scfile.app.tasks.convert.convert.auto", lambda *args: (_ for _ in ()).throw(RuntimeError()))
    failure = task._convert((entry, tmp_path / "output"))
    assert isinstance(failure, TaskItemFailure)
    assert failure.traceback is not None


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


def test_dump_replace_disambiguates_collisions(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / source.name).write_bytes(source.read_bytes())
    (right / source.name).write_bytes(source.read_bytes())
    output = tmp_path / "output"

    task = ConvertTask((left, right), (), Options(), output=output, layout=OutputLayout.DUMP, workers=2)
    summary = execute(task)

    clean = output / "document.json"
    hashed = _hashed(clean, str(right / source.name))
    assert summary.files.written == 2
    assert clean.exists()
    assert hashed.exists()

    stale = _hashed(clean, str(left / source.name))
    stale.write_bytes(b"stale")
    execute(task)

    assert not stale.exists()
    assert clean.exists()
    assert hashed.exists()


def test_dump_rename_reserves_collisions(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / source.name).write_bytes(source.read_bytes())
    (right / source.name).write_bytes(source.read_bytes())
    output = tmp_path / "output"

    task = ConvertTask(
        (left, right),
        (),
        Options(on_conflict=OnConflict.RENAME),
        output=output,
        layout=OutputLayout.DUMP,
        workers=2,
    )
    summary = execute(task)

    assert summary.files.written == 2
    assert (output / "document.json").exists()
    assert (output / "document (1).json").exists()


def test_dump_skip_skips_collisions(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / source.name).write_bytes(source.read_bytes())
    (right / source.name).write_bytes(source.read_bytes())
    output = tmp_path / "output"

    task = ConvertTask(
        (left, right),
        (),
        Options(on_conflict=OnConflict.SKIP),
        output=output,
        layout=OutputLayout.DUMP,
        workers=2,
    )
    summary = execute(task)

    assert summary.files.written == 1
    assert summary.files.skipped == 1
    assert (output / "document.json").exists()


def test_relative_replace_disambiguates_collisions(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    left = tmp_path / "left"
    right = tmp_path / "right"
    nested = Path("documents") / source.name
    (left / nested).parent.mkdir(parents=True)
    (right / nested).parent.mkdir(parents=True)
    (left / nested).write_bytes(source.read_bytes())
    (right / nested).write_bytes(source.read_bytes())
    output = tmp_path / "output"

    task = ConvertTask(
        (left, right),
        (),
        Options(),
        output=output,
        layout=OutputLayout.RELATIVE,
        workers=2,
    )
    summary = execute(task)

    clean = output / nested.with_suffix(".json")
    assert summary.files.written == 2
    assert clean.exists()
    assert len(list(clean.parent.glob("document~*.json"))) == 1
