from PySide6.QtCore import QObject, Signal
from rich.console import Console
from rich.markup import escape

from scfile import exceptions
from scfile.app.tasks import Failure, Item, Started, TaskKind
from scfile.consts import INVALID_INPUT_HINT


CONSOLE = Console()


class _Logger(QObject):
    message = Signal(str)

    def _emit(self, label: str, color: str, message: str) -> None:
        self.message.emit(f"[b {color}]{label}:[/] {escape(message)}")

    def result(self, label: str, message: str) -> None:
        self._emit(label, "green", message)

    def skipped(self, message: str) -> None:
        self._emit("SKIPPED", "blue", message)

    def error(self, message: str) -> None:
        self._emit("ERROR", "red", message)

    def exception(self, message: str) -> None:
        self._emit("UNEXPECTED ERROR", "red", message)


logger = _Logger()
logger.message.connect(CONSOLE.print)


class _Reporter:
    def __init__(self) -> None:
        self.kind: TaskKind | None = None

    def __call__(self, event: object) -> None:
        if isinstance(event, Started):
            self.kind = event.kind
            return

        if isinstance(event, Item):
            if not event.written and not event.detail:
                logger.skipped(event.source)
                return

            labels = {
                TaskKind.CONVERT: "CONVERTED",
                TaskKind.MAPCACHE: "MERGED",
                TaskKind.ANIMATE: "EXPORTED",
            }
            label = labels[self.kind] if self.kind is not None else "DONE"
            output = f" -> {', '.join(map(str, event.outputs))}" if event.outputs else ""
            logger.result(label, event.detail or f"{event.source}{output}")
            return

        if not isinstance(event, Failure):
            return

        error = event.error
        location = error.location if isinstance(error, exceptions.ScFileException) else None
        message = f"'{location or event.source}': {error}"

        if isinstance(error, exceptions.BinaryStructureError):
            logger.error(f"{message} {INVALID_INPUT_HINT}")
        elif isinstance(error, exceptions.ScFileException):
            logger.error(message)
        else:
            logger.exception(f"'{event.source}': {error!r}")

        if event.traceback:
            logger.message.emit(escape(event.traceback))


report = _Reporter()
