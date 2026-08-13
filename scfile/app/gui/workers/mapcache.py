from pathlib import Path

from PySide6.QtCore import QMutex, QMutexLocker, QObject, QThread, Signal, Slot

from scfile.convert import mapcache


class _Scanner(QObject):
    scanned = Signal(int, int, object)

    def __init__(self) -> None:
        super().__init__()
        self._mutex = QMutex()
        self._request = 0
        self._cancelled = False

    def cancel(self, request: int) -> None:
        with QMutexLocker(self._mutex):
            self._request = request
            self._cancelled = True

    def _start(self, request: int) -> bool:
        with QMutexLocker(self._mutex):
            if request != self._request:
                return False

            self._cancelled = False
            return True

    def _stopped(self) -> bool:
        with QMutexLocker(self._mutex):
            return self._cancelled

    @Slot(int, str)
    def scan(self, request: int, source: str) -> None:
        if not self._start(request):
            return

        result = mapcache.scan(Path(source), self._stopped)
        if not self._stopped():
            self.scanned.emit(request, len(mapcache.group(result.paths)), result.errors[0] if result.errors else None)


class MapCacheScanner(QObject):
    changed = Signal()
    requested = Signal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.regions = 0
        self.error: OSError | None = None
        self.busy = False
        self._request = 0

        self._thread = QThread(self)
        self._scanner = _Scanner()
        self._scanner.moveToThread(self._thread)

        self.requested.connect(self._scanner.scan)
        self._scanner.scanned.connect(self._scanned)
        self._thread.finished.connect(self._scanner.deleteLater)
        self._thread.start()

    def refresh(self, source: str) -> None:
        self._request += 1
        self._scanner.cancel(self._request)

        if not source:
            self._set(0, False, None)
            return

        self._set(0, True, None)
        self.requested.emit(self._request, source)

    @Slot(int, int, object)
    def _scanned(self, request: int, regions: int, error: object) -> None:
        if request == self._request:
            self._set(regions, False, error if isinstance(error, OSError) else None)

    def _set(self, regions: int, busy: bool, error: OSError | None) -> None:
        self.regions = regions
        self.busy = busy
        self.error = error
        self.changed.emit()

    def stop(self) -> None:
        if self._thread.isRunning():
            self._scanner.cancel(self._request + 1)
            self._thread.quit()
            self._thread.wait()
