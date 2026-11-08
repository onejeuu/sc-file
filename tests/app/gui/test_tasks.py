from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

import time

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication

from scfile.app import updates
from scfile.app.enums import TaskKind, TaskOutcome, UpdateStatus
from scfile.app.events import TaskEvent, TaskItem, TaskStarted, TaskSummary
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui import threads
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
            pass


def _wait_signal(qapp: QApplication, signal) -> None:
    received = []
    signal.connect(lambda *args: received.append(args))
    deadline = time.monotonic() + 2
    while not received and time.monotonic() < deadline:
        qapp.processEvents()
        QThread.msleep(10)
    assert received


def _wait_idle(qapp: QApplication, predicate) -> None:
    deadline = time.monotonic() + 2
    while predicate() and time.monotonic() < deadline:
        qapp.processEvents()
        QThread.msleep(10)
    assert not predicate()


def test_manager(qapp: QApplication, tmp_path: Path) -> None:
    manager = TaskManager()
    summaries: list[TaskSummary] = []
    manager.completed.connect(summaries.append)

    assert manager.start(SampleTask(tmp_path))
    assert manager.busy
    assert not manager.start(SampleTask(tmp_path))

    _wait_signal(qapp, manager.completed)
    _wait_signal(qapp, manager.busy_changed)

    assert summaries[0].outcome is TaskOutcome.COMPLETED
    manager.deleteLater()
    qapp.processEvents()


def test_cancel(qapp: QApplication) -> None:
    manager = TaskManager()
    summaries: list[TaskSummary] = []
    manager.completed.connect(summaries.append)

    assert manager.start(WaitingTask())
    manager.cancel()
    _wait_signal(qapp, manager.completed)
    _wait_signal(qapp, manager.busy_changed)

    assert summaries[0].outcome is TaskOutcome.CANCELLED
    manager.deleteLater()
    qapp.processEvents()


def test_updates(qapp: QApplication, monkeypatch) -> None:
    result = UpdateCheck(UpdateStatus.UPTODATE, "", "")
    monkeypatch.setattr(updates, "check", lambda _: result)

    checker = UpdateChecker()
    received: list[UpdateCheck] = []
    checker.status.connect(lambda *values: received.append(UpdateCheck(*values)))

    assert checker.start()
    _wait_signal(qapp, checker.status)
    _wait_idle(qapp, lambda: checker.busy)

    assert not checker.start()
    assert received == [result, result]

    checker.deleteLater()
    qapp.processEvents()


def test_job(qapp: QApplication) -> None:
    class Worker(threads.JobWorker):
        completed = Signal()

        def _run(self) -> None:
            self.completed.emit()

    worker = Worker()
    completed = []
    worker.completed.connect(lambda: completed.append(True))
    thread = threads.job(qapp, worker)
    thread.start()

    _wait_signal(qapp, worker.completed)
    _wait_signal(qapp, thread.finished)
    assert completed == [True]
