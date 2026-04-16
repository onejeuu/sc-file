import os
import traceback
from typing import Callable

from PySide6.QtCore import QObject, Signal

from scfile.enums import L

from .base import Worker, execute


class CountWorker(Worker):
    status = Signal(int, bool)

    def __init__(
        self,
        sources: list[str],
        predicate: Callable[[str], bool],
    ):
        super().__init__()
        self.sources = sources
        self.predicate = predicate

    def run(self) -> None:
        count = 0
        in_gamedir = False
        thread = self.thread()

        try:
            for source in self.sources:
                if thread and thread.isInterruptionRequested():
                    return

                if "modassets/assets" in source:
                    in_gamedir = True

                if os.path.isfile(source):
                    count += self.predicate(source)

                else:
                    for root, _, files in os.walk(source):
                        if thread and thread.isInterruptionRequested():
                            return

                        if "modassets/assets" in root.replace("\\", "/"):
                            in_gamedir = True

                        count += sum(self.predicate(file) for file in files)

            self.status.emit(count, in_gamedir)

        except Exception as err:
            print(f"{L.EXCEPTION} {repr(err)}")
            print(traceback.format_exc())

        finally:
            self.finished.emit()


class CountController(QObject):
    changed = Signal(str, int, bool)

    def __init__(self):
        super().__init__()

        self.count = 0
        self.gamedir = False
        self.is_counting = False

        self._active_thread = None

    def refresh(self, sources: list[str], predicate: Callable[[str], bool]):
        if not sources:
            self._update_state(count=0, gamedir=False, is_counting=False)
            return

        self.is_counting = True
        self.changed.emit("...", 0, True)

        self._worker = CountWorker(sources=sources, predicate=predicate)
        self._worker.status.connect(self._on_status_ready)
        self._thread = execute(self._worker)

    def _on_status_ready(self, count: int, gamedir: bool):
        self._update_state(count=count, gamedir=gamedir, is_counting=False)

    def _update_state(self, count: int, gamedir: bool, is_counting: bool):
        self.count = count
        self.gamedir = gamedir
        self.is_counting = is_counting
        text = "..." if is_counting else str(count)
        self.changed.emit(text, count, is_counting)
