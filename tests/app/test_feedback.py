from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.feedback import TaskFeedback


@pytest.fixture
def feedback() -> TaskFeedback:
    return TaskFeedback(console=Console(file=StringIO(), width=120, force_terminal=False))


def test_feedback_tracks_progress_and_finishes(feedback: TaskFeedback) -> None:
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


def test_feedback_verbose_items_are_separated(feedback: TaskFeedback) -> None:
    feedback.set_verbose(True)
    feedback(TaskStarted(TaskKind.MAPCACHE, 2))
    feedback(TaskItem("skipped"))
    feedback(TaskItem("written", Path("region.mca"), "merged"))

    assert feedback.completed == 2
    assert feedback.separated


def test_feedback_reports_expected_and_unexpected_errors(feedback: TaskFeedback) -> None:
    feedback(TaskStarted(TaskKind.ANIMATE, 3))
    feedback(TaskItemFailure("binary", exceptions.BinaryStructureError(location="binary")))
    feedback(TaskItemFailure("missing", OSError("missing")))
    feedback(TaskError(RuntimeError("broken"), source="task", traceback="trace"))

    assert feedback.completed == 2
    assert feedback.separated


def test_feedback_handles_empty_and_ignores_unknown_summary(feedback: TaskFeedback) -> None:
    feedback(TaskStarted(TaskKind.CONVERT, 0))
    feedback.finish(object())
    feedback.finish(TaskSummary(TaskKind.CONVERT, total=0))

    assert feedback.progress is None


@pytest.mark.parametrize("kind", list(TaskKind))
def test_feedback_finishes_each_task_kind(feedback: TaskFeedback, kind: TaskKind) -> None:
    summary = TaskSummary(kind, total=1)
    summary.add(TaskItem("source", Path("output")))

    feedback.finish(summary)
