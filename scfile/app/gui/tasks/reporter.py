from rich.console import Console
from rich.text import Text

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskItem, TaskItemFailure, TaskStarted
from scfile.app.gui import strings


class TaskReporter:
    def __init__(self, verbose: bool = False, console: Console | None = None):
        self.verbose = verbose
        self.console = console or Console()
        self.kind: TaskKind | None = None

    def set_verbose(self, enabled: bool) -> None:
        self.verbose = enabled

    def __call__(self, event: object) -> None:
        match event:
            case TaskStarted():
                self.kind = event.kind

            case TaskItem() if self.verbose:
                self._item(event)

            case TaskItemFailure() | TaskError():
                self.error(event.error, event.source, event.traceback)

    def _item(self, event: TaskItem) -> None:
        if event.output is None and event.detail is None:
            self._message(strings.get("task.item.skipped"), event.source, "blue")
            return

        kind = self.kind or "done"
        label = strings.get(f"task.item.{kind}")
        output = f" -> {event.output}" if event.output is not None else ""
        self._message(label, event.detail or f"{event.source}{output}", "green")

    def error(
        self,
        error: Exception,
        source: str | None = None,
        trace: str | None = None,
    ) -> None:
        location = error.location if isinstance(error, exceptions.ScFileException) else source
        prefix = f"'{location}': " if location else ""

        match error:
            case exceptions.BinaryStructureError():
                self._message("ERROR", f"{prefix}{error} {error.hint}", "red")
            case exceptions.ScFileException() | OSError():
                self._message("ERROR", f"{prefix}{error}", "red")
            case _:
                self._message("UNEXPECTED ERROR", f"'{source or 'Task'}': {error!r}", "red")

        if trace:
            self.console.print(trace, markup=False, highlight=False)

    def _message(self, label: str, text: str, color: str) -> None:
        self.console.print(Text.assemble((f"{label}: ", f"bold {color}"), text), highlight=False)
