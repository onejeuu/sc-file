import traceback
from collections.abc import Iterable

from PySide6.QtCore import QMutex, QMutexLocker, QObject, QThread, Signal, Slot

from scfile.app import files
from scfile.app.events import TaskError


class _Counter(QObject):
    counted = Signal(int, int, bool)
    failed = Signal(int, object)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()
        self._request = 0
        self._cancelled = False

    def cancel(self, request: int) -> None:
        with QMutexLocker(self._mutex):
            self._request = request
            self._cancelled = True

    def _begin(self, request: int) -> bool:
        with QMutexLocker(self._mutex):
            if request != self._request:
                return False

            self._cancelled = False
            return True

    @property
    def cancelled(self) -> bool:
        with QMutexLocker(self._mutex):
            return self._cancelled

    @Slot(int, list, tuple)
    def count(self, request: int, sources: list[str], filters: tuple[str, ...]) -> None:
        if not self._begin(request):
            return

        total = 0
        game_assets = False

        try:
            for entry in files.walk(sources, filters):
                if self.cancelled:
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
        self._request = 0

        self._thread = QThread(self)
        self._counter = _Counter()
        self._counter.moveToThread(self._thread)

        self.requested.connect(self._counter.count)
        self._counter.counted.connect(self._counted)
        self._counter.failed.connect(self._failed)
        self._thread.finished.connect(self._counter.deleteLater)
        self._thread.start()

    @property
    def text(self) -> str:
        return "..." if self.busy else f"{self.count:,}"

    def refresh(self, sources: Iterable[str], filters: Iterable[str]) -> None:
        self._request += 1
        self._counter.cancel(self._request)

        sources = list(sources)
        if not sources:
            self._set(count=0, game_assets=False, busy=False)
            return

        self._set(count=0, game_assets=False, busy=True)
        self.requested.emit(self._request, sources, tuple(filters))

    @Slot(int, int, bool)
    def _counted(self, request: int, count: int, game_assets: bool) -> None:
        if request == self._request:
            self._set(count, game_assets, busy=False)

    @Slot(int, object)
    def _failed(self, request: int, event: object) -> None:
        if request != self._request:
            return

        self._set(count=0, game_assets=False, busy=False)
        self.error.emit(event)

    def _set(self, count: int, game_assets: bool, busy: bool) -> None:
        self.count = count
        self.game_assets = game_assets
        self.busy = busy
        self.changed.emit()

    def stop(self) -> None:
        if not self._thread.isRunning():
            return

        self._counter.cancel(self._request + 1)
        self._thread.requestInterruption()
        self._thread.quit()
        self._thread.wait()
