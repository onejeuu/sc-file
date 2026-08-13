from datetime import datetime

from rich.console import Console
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


TASKS = {
    TaskKind.CONVERT: ("Converting", "Converted"),
    TaskKind.MAPCACHE: ("Merging", "Merged"),
    TaskKind.ANIMATE: ("Exporting", "Exported"),
}

OUTCOMES = {
    TaskOutcome.COMPLETED: "[green]✓ Done[/]",
    TaskOutcome.PARTIAL: "[yellow]⚠ Done[/]",
    TaskOutcome.FAILED: "[red]✗ Failed[/]",
    TaskOutcome.CANCELLED: "[yellow]■ Cancelled[/]",
}


class TaskFeedback:
    def __init__(
        self,
        verbose: bool = False,
        console: Console | None = None,
        timestamps: bool = False,
    ):
        self.verbose = verbose
        self.console = console or Console()
        self.timestamps = timestamps
        self.kind: TaskKind | None = None
        self.completed = 0
        self.progress: Progress | None = None
        self.progress_id: TaskID | None = None
        self.separated = False

    def set_verbose(self, enabled: bool) -> None:
        self.verbose = enabled

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

    def finish(self, summary: object) -> None:
        if not isinstance(summary, TaskSummary):
            return

        if summary.outcome is TaskOutcome.EMPTY:
            self._empty(summary)
            return

        if self.progress is not None and self.progress_id is not None:
            self.progress.update(self.progress_id, description=OUTCOMES[summary.outcome])
            self.console.print()
            self.progress.stop()
            self.console.print()

        action = TASKS[summary.kind][1]
        details = Text.assemble((f"{action} ", "bold green"), f"{summary.files.written:,}")

        if summary.work.failed:
            details.append(" · ")
            details.append("Failed ", style="bold red")
            details.append(f"{summary.work.failed:,}")

        if summary.files.skipped:
            details.append(" · ")
            details.append("Skipped ", style="bold blue")
            details.append(f"{summary.files.skipped:,}")

        self.console.print(details, highlight=False)
        output = str(summary.output) if summary.output is not None else "alongside source files"
        self.console.print(Text.assemble(("Output: ", "bold"), output), highlight=False)

    def _start(self, event: TaskStarted) -> None:
        if self.timestamps:
            self.console.print()
            self.console.print()
            self.console.print()
            self.console.print(datetime.now().strftime("%H:%M:%S"), style="dim", highlight=False)
            self.console.print()

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
            console=self.console,
        )
        self.progress.start()
        self.progress_id = self.progress.add_task(TASKS[event.kind][0], total=event.total)

    def _empty(self, summary: TaskSummary) -> None:
        self.console.print(Text("Nothing to convert.", style="bold cyan"), highlight=False)
        text = "No files matched the selected formats." if summary.filtered else "No supported files were found."
        self.console.print(text, highlight=False)

    def _advance(self) -> None:
        self.completed += 1
        if self.progress is not None and self.progress_id is not None:
            self.progress.update(self.progress_id, completed=self.completed)

    def _separate(self) -> None:
        if self.progress is not None and not self.separated:
            self.console.print()
            self.separated = True

    def _item(self, event: TaskItem) -> None:
        if event.output is None and event.detail is None:
            self._message("SKIPPED", event.source, "blue")
            return

        label = TASKS[self.kind][1].upper() if self.kind is not None else "DONE"
        output = f" -> {event.output}" if event.output is not None else ""
        self._message(label, event.detail or f"{event.source}{output}", "green")

    def _error(self, error: Exception, source: str | None, trace: str | None) -> None:
        location = error.location if isinstance(error, exceptions.ScFileException) else source
        prefix = f"'{location}': " if location else ""

        match error:
            case exceptions.BinaryStructureError():
                self._message("ERROR", f"{prefix}{error} {error.hint}", "red")
            case exceptions.ScFileException() | OSError():
                self._message("ERROR", f"{prefix}{error}", "red")
            case _:
                self._message("UNEXPECTED ERROR", f"Unexpected error in {source or 'task'}: {error!r}.", "red")

        if trace:
            self.console.print(trace, markup=False, highlight=False)

    def _message(self, label: str, text: str, color: str) -> None:
        self.console.print(Text.assemble((f"{label}: ", f"bold {color}"), text), highlight=False)
