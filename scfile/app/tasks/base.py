import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from threading import Event as CancelEvent
from typing import ClassVar

from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskProgress, TaskStatus, TaskSummary


type Reporter = Callable[[TaskEvent], None]


def _ignore(_: TaskEvent) -> None: ...


@dataclass(slots=True)
class TaskContext:
    cancelled: CancelEvent = field(default_factory=CancelEvent)
    _report: Reporter = field(default=_ignore, repr=False)

    @property
    def stopped(self) -> bool:
        return self.cancelled.is_set()

    def stop(self) -> None:
        self.cancelled.set()

    def advance(self, source: str | None = None, detail: str | None = None) -> None:
        self._report(TaskProgress(source, detail))

    def status(self, description: str) -> None:
        self._report(TaskStatus(description))


class Task(ABC):
    kind: ClassVar[TaskKind]

    @abstractmethod
    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]: ...


def execute(
    task: Task,
    report: Reporter = _ignore,
    context: TaskContext | None = None,
) -> TaskSummary:
    if context is None:
        context = TaskContext()

    summary = TaskSummary(task.kind)

    def emit(event: TaskEvent) -> None:
        summary.add(event)
        report(event)

    previous = context._report
    context._report = emit

    try:
        for event in task.run(context):
            emit(event)

    except Exception as error:
        event = TaskError(error, traceback=traceback.format_exc())
        emit(event)

    finally:
        context._report = previous

    summary.cancelled = context.stopped
    return summary
