import traceback

from PySide6.QtCore import QMutex, QMutexLocker, QObject, QThread, Signal, Slot

from scfile import types
from scfile.utils import files

from .logs import logger


class CounterTask(QObject):
    status = Signal(int, int, bool)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()
        self._request_id = 0
        self._abort = False

    def cancel(self, request_id: int) -> None:
        """Cancel current count and invalidate queued requests."""

        with QMutexLocker(self._mutex):
            self._request_id = request_id
            self._abort = True

    def _begin(self, request_id: int) -> bool:
        with QMutexLocker(self._mutex):
            if request_id != self._request_id:
                return False

            self._abort = False
            return True

    @property
    def abort(self) -> bool:
        with QMutexLocker(self._mutex):
            return self._abort

    @Slot(int, list, tuple)
    def count(self, request_id: int, sources: list[str], filters: types.FilesFilters):
        if not self._begin(request_id):
            return

        total = 0
        gamedir = False

        try:
            for entry in files.walk(sources, filters=filters):
                if self.abort:
                    break

                if not gamedir and "modassets\\assets" in entry.path:
                    gamedir = True

                total += 1

            if not self.abort:
                self.status.emit(request_id, total, gamedir)

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())


class CounterWorker(QObject):
    changed = Signal(str, int, bool)
    requested = Signal(int, list, tuple)

    def __init__(self):
        super().__init__()
        self._count = 0
        self._gamedir = False
        self._busy = False
        self._request_id = 0

        self._thread = QThread()
        self._task = CounterTask()
        self._task.moveToThread(self._thread)

        self.requested.connect(self._task.count)
        self._task.status.connect(self._on_done)
        self._thread.start()

    @property
    def count(self) -> int:
        return self._count

    @property
    def gamedir(self) -> bool:
        return self._gamedir

    @property
    def busy(self) -> bool:
        return self._busy

    def refresh(self, sources: list[str], filters: types.FilesFilters):
        self._request_id += 1

        self._task.cancel(self._request_id)

        if not sources:
            self._apply(count=0, gamedir=False, busy=False)
            return

        self._apply(count=0, gamedir=False, busy=True)
        self.requested.emit(self._request_id, sources, filters)

    def _on_done(self, request_id: int, count: int, gamedir: bool):
        if request_id == self._request_id:
            self._apply(count=count, gamedir=gamedir, busy=False)

    def _apply(self, count: int, gamedir: bool, busy: bool):
        self._count = count
        self._gamedir = gamedir
        self._busy = busy
        text = "..." if busy else f"{count:,}"
        self.changed.emit(text, count, busy)

    def stop(self):
        if self._thread and self._thread.isRunning():
            self._task.cancel(self._request_id + 1)
            self._thread.requestInterruption()
            self._thread.quit()
            self._thread.wait()
