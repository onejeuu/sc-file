import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from threading import Event as CancelEvent
from typing import ClassVar

from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskSummary


type Reporter = Callable[[TaskEvent], None]


def _ignore(_: TaskEvent) -> None: ...


@dataclass(slots=True)
class TaskContext:
    cancelled: CancelEvent = field(default_factory=CancelEvent)

    @property
    def stopped(self) -> bool:
        return self.cancelled.is_set()

    def stop(self) -> None:
        self.cancelled.set()


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

    try:
        for event in task.run(context):
            summary.add(event)
            report(event)

    except Exception as error:
        event = TaskError(error, traceback=traceback.format_exc())
        summary.add(event)
        report(event)

    summary.cancelled = context.stopped
    return summary
