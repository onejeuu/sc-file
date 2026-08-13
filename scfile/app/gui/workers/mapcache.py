from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from scfile.app.gui import threads
from scfile.convert import mapcache


class Scanner(QObject):
    scanned = Signal(int, int, object)

    def __init__(self, requests: threads.RequestTokens) -> None:
        super().__init__()
        self.requests = requests

    @Slot(int, str)
    def scan(self, request: int, source: str) -> None:
        if not self.requests.matches(request):
            return

        def stopped() -> bool:
            return not self.requests.matches(request)

        result = mapcache.scan(Path(source), stopped)
        if self.requests.matches(request):
            self.scanned.emit(request, len(mapcache.group(result.paths)), result.errors[0] if result.errors else None)


class MapCacheScanner(QObject):
    changed = Signal()
    requested = Signal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.regions = 0
        self.error: OSError | None = None
        self.busy = False
        self._requests = threads.RequestTokens()
        self._scanner = Scanner(self._requests)

        self.requested.connect(self._scanner.scan)
        self._scanner.scanned.connect(self._scanned)
        self._thread = threads.worker(self, self._scanner)
        self._thread.start()

    def refresh(self, source: str) -> None:
        request = self._requests.next()

        if not source:
            self._set(0, False, None)
            return

        self._set(0, True, None)
        self.requested.emit(request, source)

    @Slot(int, int, object)
    def _scanned(self, request: int, regions: int, error: object) -> None:
        if self._requests.matches(request):
            self._set(regions, False, error if isinstance(error, OSError) else None)

    def _set(self, regions: int, busy: bool, error: OSError | None) -> None:
        self.regions = regions
        self.busy = busy
        self.error = error
        self.changed.emit()

    def stop(self) -> None:
        self._requests.next()
        threads.stop(self._thread)
