import os
import traceback
from typing import Callable, TypeAlias

from PySide6.QtCore import QObject, Signal

from .base import Worker, execute
from .logs import logger


Predicate: TypeAlias = Callable[[str], bool]


class CountWorker(Worker):
    status = Signal(int, bool)

    def __init__(
        self,
        sources: list[str],
        predicate: Predicate,
    ):
        super().__init__()
        self.sources = sources
        self.predicate = predicate

    def run(self) -> None:
        count = 0
        gamedir = False
        thread = self.thread()

        try:
            for source in self.sources:
                if thread and thread.isInterruptionRequested():
                    return

                if "modassets/assets" in source:
                    gamedir = True

                if os.path.isfile(source):
                    count += self.predicate(source)

                else:
                    for root, _, files in os.walk(source):
                        if thread and thread.isInterruptionRequested():
                            return

                        if "modassets/assets" in root.replace("\\", "/"):
                            gamedir = True

                        count += sum(self.predicate(file) for file in files)

            self.status.emit(count, gamedir)

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.finished.emit()


class CountController(QObject):
    changed = Signal(str, int, bool)

    def __init__(self):
        super().__init__()
        self._count = 0
        self._gamedir = False
        self._busy = False

        self._worker = None
        self._thread = None

    @property
    def count(self) -> int:
        return self._count

    @property
    def gamedir(self) -> bool:
        return self._gamedir

    @property
    def busy(self) -> bool:
        return self._busy

    def refresh(self, sources: list[str], predicate: Predicate):
        if not sources:
            self._apply(count=0, gamedir=False, busy=False)
            return

        self._cancel()
        self._apply(count=0, gamedir=False, busy=True)

        self._worker = CountWorker(sources=sources, predicate=predicate)
        self._worker.status.connect(self._on_done)
        self._thread = execute(self._worker)

    def _cancel(self):
        if self._thread and self._thread.isRunning():
            self._thread.requestInterruption()

    def _on_done(self, count: int, gamedir: bool):
        self._apply(count=count, gamedir=gamedir, busy=False)

    def _apply(self, count: int, gamedir: bool, busy: bool):
        self._count = count
        self._gamedir = gamedir
        self._busy = busy
        text = "..." if busy else f"{count:,}"
        self.changed.emit(text, count, busy)
