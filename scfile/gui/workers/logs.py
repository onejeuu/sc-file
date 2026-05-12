from PySide6.QtCore import QObject, Signal
from rich import print

from scfile.enums import L


class _Logger(QObject):
    message = Signal(str)

    def info(self, msg: str) -> None:
        self.message.emit(f"{L.INFO} {msg}")

    def done(self, msg: str) -> None:
        self.message.emit(f"{L.DONE} {msg}")

    def error(self, msg: str) -> None:
        self.message.emit(f"{L.ERROR} {msg}")

    def exception(self, msg: str) -> None:
        self.message.emit(f"{L.EXCEPTION} {msg}")


logger = _Logger()
logger.message.connect(lambda msg: print(msg))
