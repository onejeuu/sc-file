from pathlib import Path

from scfile import exceptions
from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted
from scfile.app.tasks import TaskContext
from scfile.app.tasks.animate import AnimateTask


def test_animate_task_success(tmp_path: Path) -> None:
    output = tmp_path / "animation.glb"
    task = AnimateTask(lambda *args, **kwargs: output, tmp_path / "animation", (), output)

    events = list(task.run(TaskContext()))

    assert isinstance(events[0], TaskStarted)
    assert isinstance(events[1], TaskItem)
    assert events[1].output == output


def test_animate_task_stops_before_operation(tmp_path: Path) -> None:
    called = False

    def operation(*args, **kwargs):
        nonlocal called
        called = True

    context = TaskContext()
    context.stop()

    events = list(AnimateTask(operation, tmp_path / "animation", (), tmp_path / "output").run(context))

    assert len(events) == 1
    assert not called


def test_animate_task_reports_expected_failure(tmp_path: Path) -> None:
    error = exceptions.AnimationError("invalid")

    def operation(*args, **kwargs):
        raise error

    events = list(AnimateTask(operation, tmp_path / "animation", (), tmp_path / "output").run(TaskContext()))

    assert isinstance(events[1], TaskItemFailure)
    assert events[1].error is error
    assert events[1].traceback is None


def test_animate_task_reports_unexpected_failure(tmp_path: Path) -> None:
    error = RuntimeError("broken")

    def operation(*args, **kwargs):
        raise error

    events = list(AnimateTask(operation, tmp_path / "animation", (), tmp_path / "output").run(TaskContext()))

    assert isinstance(events[1], TaskItemFailure)
    assert events[1].error is error
    assert events[1].traceback is not None
