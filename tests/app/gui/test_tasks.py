import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import ClassVar

from PySide6.QtWidgets import QApplication

from scfile.app import updates
from scfile.app.enums import TaskKind, TaskOutcome, UpdateStatus
from scfile.app.events import TaskEvent, TaskItem, TaskStarted, TaskSummary
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.updates import UpdateChecker
from scfile.app.tasks import Task, TaskContext
from scfile.app.updates import UpdateCheck


class SampleTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    def __init__(self, output: Path):
        self.output = output

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, 1, self.output)
        if not context.stopped:
            yield TaskItem("source", self.output / "result")


class WaitingTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, 1)
        while not context.stopped:
            time.sleep(0.01)


def _wait(qapp: QApplication, predicate: Callable[[], bool]) -> None:
    limit = time.monotonic() + 2
    while not predicate() and time.monotonic() < limit:
        qapp.processEvents()
        time.sleep(0.01)

    assert predicate()


def test_task_manager(qapp: QApplication, tmp_path: Path) -> None:
    manager = TaskManager()
    summaries: list[TaskSummary] = []
    manager.completed.connect(summaries.append)

    assert manager.start(SampleTask(tmp_path))
    assert manager.busy
    assert not manager.start(SampleTask(tmp_path))

    _wait(qapp, lambda: bool(summaries))
    _wait(qapp, lambda: not manager.busy)

    assert summaries[0].outcome is TaskOutcome.COMPLETED
    manager.deleteLater()
    qapp.processEvents()


def test_task_cancel(qapp: QApplication) -> None:
    manager = TaskManager()
    summaries: list[TaskSummary] = []
    manager.completed.connect(summaries.append)

    assert manager.start(WaitingTask())
    manager.cancel()
    _wait(qapp, lambda: bool(summaries))
    _wait(qapp, lambda: not manager.busy)

    assert summaries[0].outcome is TaskOutcome.CANCELLED
    manager.deleteLater()
    qapp.processEvents()


def test_update_checker(qapp: QApplication, monkeypatch) -> None:
    result = UpdateCheck(UpdateStatus.UPTODATE, "", "")
    monkeypatch.setattr(updates, "check", lambda _: result)

    checker = UpdateChecker()
    received: list[UpdateCheck] = []
    checker.status.connect(lambda *values: received.append(UpdateCheck(*values)))

    assert checker.start()
    _wait(qapp, lambda: bool(received))
    _wait(qapp, lambda: not checker.busy)

    assert not checker.start()
    assert received == [result, result]

    checker.deleteLater()
    qapp.processEvents()
