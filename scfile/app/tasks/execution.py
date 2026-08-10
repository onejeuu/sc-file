"""Task execution and cancellation."""

import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from threading import Event as CancelEvent
from typing import ClassVar

from scfile.app.enums import TaskKind

from .events import TaskError, TaskEvent, TaskSummary


type Reporter = Callable[[TaskEvent], None]


def _ignore(_: TaskEvent) -> None: ...


@dataclass(slots=True)
class TaskContext:
    """Cancellation state shared by one task run."""

    cancelled: CancelEvent = field(default_factory=CancelEvent)

    @property
    def stopped(self) -> bool:
        return self.cancelled.is_set()

    def stop(self) -> None:
        self.cancelled.set()


class Task(ABC):
    """Application operation that yields facts about its execution."""

    kind: ClassVar[TaskKind]

    @abstractmethod
    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        """Yield task facts until completion or cancellation."""


def execute(
    task: Task,
    report: Reporter = _ignore,
    context: TaskContext | None = None,
) -> TaskSummary:
    """Run one task and collect its reported facts."""

    if context is None:
        context = TaskContext()
    summary = TaskSummary(task.kind)

    try:
        for event in task.run(context):
            summary.add(event)
            report(event)

    except Exception as error:
        event = TaskError(error, traceback.format_exc())
        summary.add(event)
        report(event)

    summary.cancelled = context.stopped
    return summary
