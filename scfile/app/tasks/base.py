import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from threading import Event as CancelEvent
from typing import ClassVar

from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskProgress, TaskSummary


type Reporter = Callable[[TaskEvent], None]


def _ignore(_: TaskEvent) -> None: ...


def _ignore_progress(_: TaskProgress) -> None: ...


@dataclass(slots=True)
class TaskContext:
    cancelled: CancelEvent = field(default_factory=CancelEvent)
    _progress: Callable[[TaskProgress], None] = field(default=_ignore_progress, repr=False)

    @property
    def stopped(self) -> bool:
        return self.cancelled.is_set()

    def stop(self) -> None:
        self.cancelled.set()

    def advance(self, source: str | None = None) -> None:
        self._progress(TaskProgress(source))


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
    progress = context._progress
    context._progress = report

    try:
        for event in task.run(context):
            summary.add(event)
            report(event)

    except Exception as error:
        event = TaskError(error, traceback=traceback.format_exc())
        summary.add(event)
        report(event)

    finally:
        context._progress = progress

    summary.cancelled = context.stopped
    return summary
