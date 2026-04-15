import os
import traceback
from typing import Callable

from PySide6.QtCore import QObject, Signal

from scfile.enums import L

from .base import Worker, execute


class CountWorker(Worker):
    count = Signal(int)

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

        try:
            for source in self.sources:
                if os.path.isfile(source):
                    count += self.predicate(source)
                else:
                    count += sum(self.predicate(file) for _, _, files in os.walk(source) for file in files)

            self.count.emit(count)

        except Exception as err:
            print(f"{L.EXCEPTION} {repr(err)}")
            print(traceback.format_exc())

        finally:
            self.finished.emit()


class CountController(QObject):
    changed = Signal(str, int, bool)

    def __init__(self):
        super().__init__()

        self._count = 0
        self._is_counting = False
        self._active_thread = None

    @property
    def count(self) -> int:
        return self._count

    def refresh(self, sources: list[str], predicate: Callable[[str], bool]):
        if not sources:
            self._update_state(0, False)
            return

        self._is_counting = True
        self.changed.emit("...", 0, True)

        self._worker = CountWorker(sources=sources, predicate=predicate)
        self._worker.count.connect(self._on_count_ready)
        self._thread = execute(self._worker)

    def _on_count_ready(self, count: int):
        self._update_state(count, False)

    def _update_state(self, count: int, is_counting: bool):
        self._count = count
        self._is_counting = is_counting
        status_text = "..." if is_counting else str(count)
        self.changed.emit(status_text, count, is_counting)
