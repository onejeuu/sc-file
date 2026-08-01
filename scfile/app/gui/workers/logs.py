from PySide6.QtCore import QObject, Signal
from rich import print

from scfile import exceptions
from scfile.app.tasks import Failure
from scfile.consts import INVALID_INPUT_HINT
from scfile.enums import L


class _Logger(QObject):
    message = Signal(str)

    def error(self, msg: str) -> None:
        self.message.emit(f"{L.ERROR} {msg}")

    def exception(self, msg: str) -> None:
        self.message.emit(f"{L.EXCEPTION} {msg}")


logger = _Logger()
logger.message.connect(lambda msg: print(msg))


def report(event: object) -> None:
    """Render a task event through the current console logger."""

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
        logger.message.emit(event.traceback)
