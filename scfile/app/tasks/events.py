"""Task facts and aggregate statistics."""

from dataclasses import dataclass, field
from pathlib import Path

from scfile.app.enums import TaskKind, TaskOutcome


@dataclass(frozen=True, slots=True)
class TaskStarted:
    """First event emitted by every task run."""

    kind: TaskKind
    total: int
    output: Path | None = None


@dataclass(frozen=True, slots=True)
class TaskItem:
    """Completed source item and its optional output."""

    source: str
    output: Path | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class TaskFailure:
    """Failure of one source item."""

    source: str
    error: Exception
    traceback: str | None = None


@dataclass(frozen=True, slots=True)
class TaskError:
    """Task-level failure outside an individual work item."""

    error: Exception
    traceback: str | None = None


type TaskEvent = TaskStarted | TaskItem | TaskFailure | TaskError


@dataclass(slots=True)
class TaskWork:
    """Statistics of processed work units."""

    completed: int = 0
    failed: int = 0


@dataclass(slots=True)
class TaskFiles:
    """Statistics of output files."""

    written: int = 0
    skipped: int = 0


@dataclass(slots=True)
class TaskSummary:
    """Reduce a task event stream into final statistics."""

    kind: TaskKind
    total: int | None = None
    output: Path | None = None
    work: TaskWork = field(default_factory=TaskWork)
    files: TaskFiles = field(default_factory=TaskFiles)
    cancelled: bool = False

    @property
    def outcome(self) -> TaskOutcome:
        """Return the final state represented by collected facts."""

        if self.cancelled:
            return TaskOutcome.CANCELLED

        if not self.work.completed and not self.work.failed:
            return TaskOutcome.EMPTY

        if not self.files.written and self.work.failed:
            return TaskOutcome.FAILED

        if self.work.failed or self.files.skipped:
            return TaskOutcome.PARTIAL

        return TaskOutcome.COMPLETED

    def add(self, event: TaskEvent) -> None:
        """Include one fact from the task stream."""

        match event:
            case TaskStarted():
                self.kind = event.kind
                self.total = event.total
                self.output = event.output

            case TaskItem(output=None):
                self.work.completed += 1
                self.files.skipped += 1

            case TaskItem():
                self.work.completed += 1
                self.files.written += 1

            case TaskFailure():
                self.work.completed += 1
                self.work.failed += 1

            case TaskError():
                self.work.failed += 1
