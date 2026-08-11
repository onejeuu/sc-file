from typing import NamedTuple

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text

from scfile import exceptions
from scfile.app.enums import TaskKind, TaskOutcome
from scfile.app.events import TaskError, TaskItem, TaskItemFailure, TaskStarted, TaskSummary

from .console import CONSOLE, error, unexpected


class TaskText(NamedTuple):
    running: str
    item: str


TASK_TEXT = {
    TaskKind.CONVERT: TaskText("Converting", "Converted"),
    TaskKind.MAPCACHE: TaskText("Merging", "Merged"),
    TaskKind.ANIMATE: TaskText("Exporting", "Exported"),
}

OUTCOME_TEXT = {
    TaskOutcome.COMPLETED: "[green]✓ Done[/]",
    TaskOutcome.PARTIAL: "[yellow]⚠ Done[/]",
    TaskOutcome.FAILED: "[red]✗ Failed[/]",
    TaskOutcome.CANCELLED: "[yellow]■ Cancelled[/]",
}


class TaskFeedback:
    """Present a task event stream in the terminal."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.kind: TaskKind | None = None
        self.completed = 0
        self.progress: Progress | None = None
        self.progress_id: TaskID | None = None
        self.separated = False

    def __call__(self, event: object) -> None:
        match event:
            case TaskStarted():
                self._start(event)
            case TaskItem():
                self._advance()
                if self.verbose:
                    self._separate()
                    self._item(event)
            case TaskItemFailure():
                self._advance()
                self._separate()
                self._error(event.error, event.source, event.traceback)
            case TaskError():
                self._separate()
                self._error(event.error, event.source, event.traceback)

    def _start(self, event: TaskStarted) -> None:
        self.kind = event.kind
        self.completed = 0
        self.separated = False

        if event.total == 0:
            return

        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=CONSOLE,
        )
        self.progress.start()
        self.progress_id = self.progress.add_task(TASK_TEXT[event.kind].running, total=event.total)

    def _advance(self) -> None:
        self.completed += 1
        if self.progress is None or self.progress_id is None:
            return

        self.progress.update(self.progress_id, completed=self.completed)

    def _separate(self) -> None:
        if self.progress is None or self.separated:
            return

        CONSOLE.print()
        self.separated = True

    def _item(self, event: TaskItem) -> None:
        if event.output is None:
            line = Text("SKIPPED: ", style="bold blue")
            line.append(event.source)
        else:
            label = TASK_TEXT[self.kind].item if self.kind is not None else "DONE"
            line = Text(f"{label.upper()}: ", style="bold green")
            line.append(event.detail or f"{event.source} -> {event.output}")

        CONSOLE.print(line, highlight=False)

    def _error(
        self,
        exception: Exception,
        source: str | None,
        trace: str | None,
    ) -> None:
        location = exception.location if isinstance(exception, exceptions.ScFileException) else source
        prefix = f"'{location}': " if location else ""

        match exception:
            case exceptions.BinaryStructureError():
                error(f"{prefix}{exception} {exception.hint}")
            case exceptions.ScFileException():
                error(f"{prefix}{exception}")
            case OSError():
                error(f"{prefix}{exception}")
            case _:
                unexpected(f"Unexpected error in {source or 'task'}: {exception!r}.")

        if trace:
            CONSOLE.print(trace, markup=False, highlight=False)

    def finish(self, summary: TaskSummary) -> None:
        if summary.outcome is TaskOutcome.EMPTY:
            CONSOLE.print(Text("∅ No matching files.", style="bold cyan"), highlight=False)
            return

        if self.progress is not None and self.progress_id is not None:
            self.progress.update(self.progress_id, description=OUTCOME_TEXT[summary.outcome])
            CONSOLE.print()
            self.progress.stop()
            CONSOLE.print()

        details = Text.assemble(
            (TASK_TEXT[summary.kind].item + " ", "bold green"),
            f"{summary.files.written:,}",
        )

        if summary.work.failed:
            details.append(" · ")
            details.append("Failed ", style="bold red")
            details.append(f"{summary.work.failed:,}")

        if summary.files.skipped:
            details.append(" · ")
            details.append("Skipped ", style="bold blue")
            details.append(f"{summary.files.skipped:,}")

        CONSOLE.print(details, highlight=False)

        output = str(summary.output) if summary.output is not None else "alongside source files"
        CONSOLE.print(Text.assemble(("Output: ", "bold"), output), highlight=False)
