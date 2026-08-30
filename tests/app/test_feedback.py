from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskItem, TaskItemFailure, TaskProgress, TaskStarted, TaskSummary
from scfile.app.feedback import TaskFeedback


@pytest.fixture
def feedback() -> TaskFeedback:
    return TaskFeedback(console=Console(file=StringIO(), width=120, force_terminal=False))


def test_progress(feedback: TaskFeedback) -> None:
    feedback(TaskStarted(TaskKind.CONVERT, 2, Path("output")))
    feedback(TaskItem("first", Path("output/first")))
    feedback(TaskItem("second"))

    summary = TaskSummary(TaskKind.CONVERT, total=2, output=Path("output"))
    summary.add(TaskItem("first", Path("output/first")))
    summary.add(TaskItem("second"))
    feedback.finish(summary)

    assert feedback.completed == 2
    assert feedback.progress is not None
    assert feedback.progress.live.is_started is False


def test_subprogress(feedback: TaskFeedback) -> None:
    feedback(TaskStarted(TaskKind.MAPMERGE, 2))
    feedback(TaskProgress("tile.ol"))
    feedback(TaskItem("tile.ol", Path("map.jpg")))

    assert feedback.completed == 2


def test_verbose(feedback: TaskFeedback) -> None:
    feedback.set_verbose(True)
    feedback(TaskStarted(TaskKind.MAPCACHE, 2))
    feedback(TaskItem("skipped"))
    feedback(TaskItem("written", Path("region.mca"), "merged"))

    assert feedback.completed == 2
    assert feedback.separated


def test_errors(feedback: TaskFeedback) -> None:
    feedback(TaskStarted(TaskKind.ANIMATE, 3))
    feedback(TaskItemFailure("binary", exceptions.BinaryStructureError(location="binary")))
    feedback(TaskItemFailure("missing", OSError("missing")))
    feedback(TaskError(RuntimeError("broken"), source="task", traceback="trace"))

    assert feedback.completed == 2
    assert feedback.separated


def test_empty(feedback: TaskFeedback) -> None:
    feedback(TaskStarted(TaskKind.CONVERT, 0))
    feedback.finish(object())
    feedback.finish(TaskSummary(TaskKind.CONVERT, total=0))

    assert feedback.progress is None


def test_summary(feedback: TaskFeedback) -> None:
    summary = TaskSummary(TaskKind.CONVERT, total=2)
    summary.add(TaskItem("written", Path("output")))
    summary.add(TaskItemFailure("broken", RuntimeError()))

    feedback.finish(summary)


def test_item(feedback: TaskFeedback) -> None:
    feedback._item(TaskItem("source", Path("output")))

    assert feedback.kind is None


def test_idle(feedback: TaskFeedback) -> None:
    feedback._advance()
    feedback._separate()

    assert feedback.completed == 1


@pytest.mark.parametrize("kind", list(TaskKind))
def test_kinds(feedback: TaskFeedback, kind: TaskKind) -> None:
    summary = TaskSummary(kind, total=1)
    summary.add(TaskItem("source", Path("output")))

    feedback.finish(summary)
