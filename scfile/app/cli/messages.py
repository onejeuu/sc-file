"""Command-line feedback rendering."""

from collections.abc import Iterable

from rich.console import Console, RenderableType
from rich.markup import escape
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress as RichProgress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text

from scfile import exceptions, types
from scfile.app.tasks import (
    PROGRESS_THRESHOLD,
    Failure,
    Item,
    Progress,
    Started,
    Summary,
    TaskKind,
)
from scfile.consts import INVALID_INPUT_HINT
from scfile.enums import FileFormat
from scfile.options import HandlerOptions
from scfile.registry import REGISTRY
from scfile.structures.models import Feature, Features


CONSOLE = Console()


class _TaskProgress(RichProgress):
    """Live progress with optional separation from streamed messages."""

    separated = False

    def get_renderables(self) -> Iterable[RenderableType]:
        if self.separated:
            yield Text()
        yield from super().get_renderables()


def _message(
    label: str,
    message: str,
    color: str,
    console: Console = CONSOLE,
) -> None:
    console.print(f"[bold {color}]{label}:[/] {escape(message)}", highlight=False)


def warning(message: str) -> None:
    """Render a command-line warning."""

    _message("WARN", message, "yellow")


def warn_unsupported_features(
    formats: types.Formats,
    options: HandlerOptions,
) -> None:
    """Warn when explicitly selected formats omit requested model data."""

    requested: Features = ()
    if options.skeleton_enabled:
        requested += (Feature.SKELETON,)

    if options.animation:
        requested += (Feature.ANIMATION,)

    unsupported: dict[FileFormat, Features] = {}
    for fmt in formats:
        features = tuple(feature for feature in requested if not REGISTRY.formats[fmt].supports(feature))
        if features:
            unsupported[fmt] = features

    if not unsupported:
        return

    details = "; ".join(f"{fmt.upper()} ({', '.join(features)})" for fmt, features in unsupported.items())
    warning(f"Requested model feature is not supported by: {details}.")


def task_message(
    event: object,
    console: Console = CONSOLE,
    kind: TaskKind | None = None,
) -> None:
    """Render one application task event."""

    if isinstance(event, Item):
        labels = {
            TaskKind.CONVERT: "CONVERTED",
            TaskKind.MAPCACHE: "MERGED",
            TaskKind.ANIMATE: "EXPORTED",
        }
        label = labels[kind] if kind is not None else "DONE"
        if event.detail:
            _message(label, event.detail, "green", console)
        elif event.written:
            output = f" -> {', '.join(map(str, event.outputs))}" if event.outputs else ""
            _message(label, f"{event.source}{output}", "green", console)
        else:
            _message("SKIPPED", event.source, "blue", console)
        return

    if not isinstance(event, Failure):
        return

    error = event.error
    location = error.location if isinstance(error, exceptions.ScFileException) else None
    message = f"'{location or event.source}': {error}"
    if isinstance(error, exceptions.BinaryStructureError):
        _message("ERROR", f"{message} {INVALID_INPUT_HINT}", "red", console)
    elif isinstance(error, exceptions.ScFileException):
        _message("ERROR", message, "red", console)
    else:
        _message("UNEXPECTED ERROR", f"File '{event.source}' {error!r}. {INVALID_INPUT_HINT}", "red", console)

    if event.traceback:
        console.print(event.traceback, markup=False, highlight=False)


def _plural(count: int, singular: str, plural: str | None = None) -> str:
    return singular if count == 1 else (plural or f"{singular}s")


class TaskFeedback:
    """Render task messages, adaptive live progress, and final results."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = CONSOLE
        self._started: Started | None = None
        self._progress: _TaskProgress | None = None
        self._progress_id: TaskID | None = None

    def __call__(self, event: object) -> None:
        if isinstance(event, Started):
            self._start(event)
            return

        if isinstance(event, Progress):
            self._update(event)
            return

        if isinstance(event, Failure) or self.verbose:
            self._separate_progress()
            kind = self._started.kind if self._started else None
            task_message(event, self.console, kind)

    def _start(self, event: Started) -> None:
        self._started = event
        if event.total < PROGRESS_THRESHOLD:
            return

        descriptions = {
            TaskKind.CONVERT: "Converting",
            TaskKind.MAPCACHE: "Merging",
            TaskKind.ANIMATE: "Exporting",
        }
        description = descriptions[event.kind]
        self._progress = _TaskProgress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        )
        self._progress.start()
        self._progress_id = self._progress.add_task(description, total=event.total)

    def _separate_progress(self) -> None:
        if self._progress is None or self._progress.separated:
            return

        self._progress.separated = True
        self._progress.refresh()

    def _update(self, event: Progress) -> None:
        if self._progress is not None and self._progress_id is not None:
            description = "Done" if event.total is not None and event.completed >= event.total else None
            self._progress.update(self._progress_id, completed=event.completed, description=description)

    def finish(self, summary: Summary) -> None:
        """Close live progress and render operation-specific task results."""

        if self._progress is not None:
            self._progress.stop()

        color = "yellow" if summary.cancelled or summary.failed else "green"
        if summary.cancelled:
            cancellations = {
                TaskKind.CONVERT: (
                    f"Conversion cancelled after {summary.completed:,} of {summary.total:,} source files"
                ),
                TaskKind.MAPCACHE: f"Merge cancelled after {summary.completed:,} of {summary.total:,} regions",
                TaskKind.ANIMATE: "Animation export cancelled",
            }
            result = cancellations[summary.kind]
        elif summary.kind is TaskKind.CONVERT:
            converted = summary.succeeded
            if not converted:
                result = "No files converted"
            elif summary.failed:
                result = f"Converted {converted:,} of {summary.total:,} source files"
            elif not summary.skipped and summary.written == converted:
                result = f"Converted {converted:,} {_plural(converted, 'file')}"
            else:
                result = f"Converted {converted:,} {_plural(converted, 'source file')}"
        elif summary.kind is TaskKind.MAPCACHE:
            if summary.failed and not summary.total:
                result = "Region merge failed"
            elif summary.failed:
                result = f"Merged {summary.written:,} of {summary.total:,} regions"
            else:
                result = f"Merged {summary.written:,} {_plural(summary.written, 'region')}"
        else:
            result = "Exported animated model" if summary.written else "Animation export failed"

        self.console.print(f"[bold {color}]{result}[/]", highlight=False)

        if summary.kind is TaskKind.CONVERT and (
            summary.failed or summary.skipped or summary.written != summary.succeeded
        ):
            details = []
            if summary.written:
                details.append(f"[green]Exported {summary.written:,}[/]")
            if summary.skipped:
                details.append(f"[blue]Skipped {summary.skipped:,}[/]")
            if summary.failed:
                details.append(f"[red]Failed {summary.failed:,}[/]")
            if details:
                self.console.print(f"[bold]Stats:[/] {' · '.join(details)}", highlight=False)
        elif summary.kind is TaskKind.MAPCACHE and summary.failed:
            self.console.print(f"Failed {summary.failed:,}", highlight=False)

        if summary.output is None:
            output = "alongside source files"
        else:
            output = str(summary.output)
        self.console.print(f"[bold]Output:[/] {escape(output)}", highlight=False)
