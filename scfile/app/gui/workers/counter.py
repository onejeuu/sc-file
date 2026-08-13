import traceback
from collections.abc import Iterable

from PySide6.QtCore import QObject, Signal, Slot

from scfile.app import files
from scfile.app.events import TaskError
from scfile.app.gui import threads


class _Counter(QObject):
    counted = Signal(int, int, bool)
    failed = Signal(int, object)

    def __init__(self, requests: threads.RequestTokens):
        super().__init__()
        self.requests = requests

    @Slot(int, list, tuple)
    def count(self, request: int, sources: list[str], filters: tuple[str, ...]) -> None:
        if not self.requests.matches(request):
            return

        total = 0
        game_assets = False

        try:
            for entry in files.walk(sources, filters):
                if not self.requests.matches(request):
                    return

                path = entry.path.replace("\\", "/").lower()
                game_assets = game_assets or "/modassets/assets/" in f"/{path.strip('/')}/"
                total += 1

            self.counted.emit(request, total, game_assets)

        except Exception as error:
            event = TaskError(error, traceback=traceback.format_exc())
            self.failed.emit(request, event)


class FileCounter(QObject):
    changed = Signal()
    error = Signal(object)
    requested = Signal(int, list, tuple)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.count = 0
        self.game_assets = False
        self.busy = False
        self._requests = threads.RequestTokens()
        self._counter = _Counter(self._requests)

        self.requested.connect(self._counter.count)
        self._counter.counted.connect(self._counted)
        self._counter.failed.connect(self._failed)
        self._thread = threads.worker(self, self._counter)
        self._thread.start()

    @property
    def text(self) -> str:
        return "..." if self.busy else f"{self.count:,}"

    def refresh(self, sources: Iterable[str], filters: Iterable[str]) -> None:
        request = self._requests.next()

        sources = list(sources)
        if not sources:
            self._set(count=0, game_assets=False, busy=False)
            return

        self._set(count=0, game_assets=False, busy=True)
        self.requested.emit(request, sources, tuple(filters))

    @Slot(int, int, bool)
    def _counted(self, request: int, count: int, game_assets: bool) -> None:
        if self._requests.matches(request):
            self._set(count, game_assets, busy=False)

    @Slot(int, object)
    def _failed(self, request: int, event: object) -> None:
        if not self._requests.matches(request):
            return

        self._set(count=0, game_assets=False, busy=False)
        self.error.emit(event)

    def _set(self, count: int, game_assets: bool, busy: bool) -> None:
        self.count = count
        self.game_assets = game_assets
        self.busy = busy
        self.changed.emit()

    def stop(self) -> None:
        self._requests.next()
        threads.stop(self._thread)
