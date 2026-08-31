from datetime import datetime
from pathlib import Path
from typing import Iterable, NamedTuple

from rich.console import Console, RenderableType
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    Task,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)
from rich.spinner import Spinner
from rich.table import Column
from rich.text import Text

from scfile import exceptions
from scfile.app.enums import TaskKind, TaskOutcome
from scfile.app.events import TaskError, TaskItem, TaskItemFailure, TaskProgress, TaskStarted, TaskSummary


class TaskText(NamedTuple):
    header: str
    running: str
    finished: str


class Marker(NamedTuple):
    icon: str
    color: str


class StatusColumn(ProgressColumn):
    def __init__(self) -> None:
        super().__init__(table_column=Column(width=1, no_wrap=True))
        self.spinner = Spinner("dots", style="cyan")

    def render(self, task: Task) -> RenderableType:
        marker = task.fields.get("marker")
        if isinstance(marker, Marker):
            return Text(marker.icon, style=f"bold {marker.color}")
        return self.spinner.render(task.get_time())


class ProgressBlock(Progress):
    def get_renderables(self) -> Iterable[RenderableType]:
        yield Text()
        yield from super().get_renderables()
        yield Text()


class ElapsedColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        minutes, seconds = divmod(task.elapsed or 0, 60)
        prefix = f"{int(minutes)}m " if minutes else ""
        return Text(f"{prefix}{seconds:.1f}s", style="progress.elapsed")


SUCCESS = Marker("✓", "green")
PARTIAL = Marker("!", "yellow")
FAILURE = Marker("×", "red")
CANCELLED = Marker("~", "yellow")
SKIPPED = Marker("•", "blue")

TASKS: dict[TaskKind, TaskText] = {
    TaskKind.CONVERT: TaskText("Conversion", "Converting", "Converted"),
    TaskKind.ANIMATE: TaskText("Animation export", "Exporting", "Exported"),
    TaskKind.MAPCACHE: TaskText("Map cache merge", "Merging", "Merged"),
    TaskKind.MAPTILES: TaskText("Map tiles assembly", "Assembling", "Assembled"),
}

OUTCOMES: dict[TaskOutcome, tuple[str, Marker]] = {
    TaskOutcome.COMPLETED: ("Done", SUCCESS),
    TaskOutcome.PARTIAL: ("Done", PARTIAL),
    TaskOutcome.FAILED: ("Failed", FAILURE),
    TaskOutcome.CANCELLED: ("Cancelled", CANCELLED),
}


def _error_message(error: Exception) -> str:
    match error:
        case exceptions.BinaryStructureError():
            return f"{error} {error.hint}"

        case exceptions.ScFileException() | OSError():
            return str(error)

        case _:
            return f"Unexpected error: {error!r}."


def _path_string(value: str | Path) -> str:
    return value.as_posix() if isinstance(value, Path) else value.replace("\\", "/")


def _path(value: str | Path, marker: Marker | None = None) -> Text:
    path = _path_string(value)
    directory, separator, filename = path.rpartition("/")
    filename_style = f"bold {marker.color}" if marker is not None else "bold white"

    if not separator or not filename:
        return Text(path, style=filename_style)

    return Text.assemble(
        (f"{directory}{separator}", "not bold dim default"),
        (filename, filename_style),
    )


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

    def set_verbose(self, enabled: bool) -> None:
        self.verbose = enabled

    def __call__(self, event: object) -> None:
        match event:
            case TaskStarted():
                self._start(event)

            case TaskProgress():
                self._advance()

            case TaskItem():
                self._advance()
                if self.verbose:
                    self._item(event)

            case TaskItemFailure():
                self._advance()
                self._error(event.error, event.source, event.traceback)

            case TaskError():
                self._error(event.error, event.source, event.traceback)

    def finish(self, summary: object) -> None:
        if not isinstance(summary, TaskSummary):
            return

        if summary.outcome is TaskOutcome.EMPTY:
            self._empty(summary)
            return

        self._finish_progress(summary.outcome)
        self._summary(summary)

    def _start(self, event: TaskStarted) -> None:
        if self.timestamps:
            self._header(event)

        self.kind = event.kind
        self.completed = 0

        if event.total == 0:
            return

        progress = (
            (
                BarColumn(bar_width=32),
                TaskProgressColumn(),
                MofNCompleteColumn(),
            )
            if event.total > 1
            else ()
        )
        self.progress = ProgressBlock(
            StatusColumn(),
            TextColumn(
                "{task.description}",
                style="bold",
                table_column=Column(width=10, no_wrap=True),
            ),
            *progress,
            ElapsedColumn(),
            console=self.console,
        )
        self.progress.start()
        self.progress_id = self.progress.add_task(TASKS[event.kind].running, total=event.total)

    def _header(self, event: TaskStarted) -> None:
        text = Text.assemble(
            "\n\n\n",
            (datetime.now().strftime("%H:%M:%S"), "dim"),
            "\n",
            TASKS[event.kind].header,
            "\n",
        )
        self.console.print(text, highlight=False)

    def _finish_progress(self, outcome: TaskOutcome) -> None:
        if self.progress is None or self.progress_id is None:
            return

        label, marker = OUTCOMES[outcome]
        self.progress.update(
            self.progress_id,
            description=f"[{marker.color}]{label}[/]",
            marker=marker,
        )
        self.progress.stop()

    def _summary(self, summary: TaskSummary) -> None:
        entries: list[Text] = []

        if summary.files.written:
            entries.append(
                Text(
                    f"{summary.files.written:,} {TASKS[summary.kind].finished.lower()}",
                    style=f"bold {SUCCESS.color}",
                )
            )

        if summary.work.failed:
            entries.append(Text(f"{summary.work.failed:,} failed", style=f"bold {FAILURE.color}"))

        if summary.files.skipped:
            entries.append(Text(f"{summary.files.skipped:,} skipped", style=f"bold {SKIPPED.color}"))

        summary_text = Text.assemble(
            ("Summary: ", "bold white"),
            Text(", ", style="bold white").join(entries),
        )
        output = summary.output.as_posix() if summary.output is not None else "alongside source files"
        output_text = Text.assemble(
            ("Output: ", "bold white"),
            (output, "cyan"),
        )

        self.console.print(summary_text, highlight=False)
        self.console.print(output_text, highlight=False)

    def _empty(self, summary: TaskSummary) -> None:
        title = Text("Nothing to convert.", style="bold cyan")
        reason = Text(
            "No files matched the selected formats." if summary.filtered else "No supported files were found."
        )
        self.console.print(title, highlight=False)
        self.console.print(reason, highlight=False)

    def _advance(self) -> None:
        self.completed += 1
        if self.progress is not None and self.progress_id is not None:
            self.progress.update(self.progress_id, completed=self.completed)

    def _item(self, event: TaskItem) -> None:
        if event.output is None and event.detail is None:
            text = self._line(
                event.source,
                Text("Skip", style=f"bold {SKIPPED.color}"),
                SKIPPED,
            )
        else:
            content = (
                _path(event.output, SUCCESS)
                if event.output is not None
                else Text(event.detail or "", style=f"bold {SUCCESS.color}")
            )
            detail = event.detail if event.output is not None else None
            text = self._line(event.source, content, SUCCESS, detail)

        self.console.print(text, highlight=False)

    def _error(self, error: Exception, source: str | None, trace: str | None) -> None:
        location = source or (error.location if isinstance(error, exceptions.ScFileException) else None)
        message = _error_message(error)
        text = (
            self._line(location, Text(message, style=f"bold {FAILURE.color}"), FAILURE)
            if location is not None
            else Text(message, style=FAILURE.color)
        )
        self.console.print(text, highlight=False)

        if trace:
            self.console.print(trace, markup=False, highlight=False)

    def _line(
        self,
        source: str | Path,
        content: Text,
        marker: Marker,
        detail: str | None = None,
    ) -> Text:
        suffix = (
            Text.assemble(
                (" · ", f"bold dim {marker.color}"),
                (detail, f"bold dim {marker.color}"),
            )
            if detail is not None
            else Text()
        )

        return Text.assemble(
            (f"{marker.icon} ", f"bold {marker.color}"),
            _path(source, marker),
            (" → ", "bold white"),
            content,
            suffix,
        )
