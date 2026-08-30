from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from scfile.app.gui import threads
from scfile.convert import mapcache


class Scanner(QObject):
    scanned = Signal(int, int, int, bool, object)

    def __init__(self, requests: threads.RequestTokens) -> None:
        super().__init__()
        self.requests = requests

    @Slot(int, str, str)
    def scan(self, request: int, source: str, output: str) -> None:
        if not self.requests.matches(request):
            return

        def stopped() -> bool:
            return not self.requests.matches(request)

        result = mapcache.scan(Path(source), stopped)
        regions = mapcache.group(result.paths)
        existing: set[mapcache.Region] = set()

        if output:
            existing = {
                key
                for path in Path(output).glob(f"*{mapcache.MCA_SUFFIX}")
                if path.is_file()
                if (key := mapcache.Region.parse(path.stem.removeprefix(mapcache.MCA_PREFIX)))
            }

        replaces = bool(regions.keys() & existing)

        if self.requests.matches(request):
            self.scanned.emit(
                request,
                len(result.paths),
                len(regions),
                replaces,
                result.errors[0] if result.errors else None,
            )


class MapCacheScanner(QObject):
    changed = Signal()
    requested = Signal(int, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.files = 0
        self.regions = 0
        self.replaces = False
        self.error: OSError | None = None
        self.busy = False
        self._requests = threads.RequestTokens()
        self._scanner = Scanner(self._requests)

        self.requested.connect(self._scanner.scan)
        self._scanner.scanned.connect(self._scanned)
        self._thread = threads.worker(self, self._scanner)
        self._thread.start()

    def refresh(self, source: str, output: str) -> None:
        request = self._requests.next()

        if not source:
            self._set(0, 0, False, False, None)
            return

        self._set(0, 0, False, True, None)
        self.requested.emit(request, source, output)

    @Slot(int, int, int, bool, object)
    def _scanned(self, request: int, files: int, regions: int, replaces: bool, error: object) -> None:
        if self._requests.matches(request):
            self._set(files, regions, replaces, False, error if isinstance(error, OSError) else None)

    def _set(self, files: int, regions: int, replaces: bool, busy: bool, error: OSError | None) -> None:
        self.files = files
        self.regions = regions
        self.replaces = replaces
        self.busy = busy
        self.error = error
        self.changed.emit()

    def stop(self) -> None:
        self._requests.next()
        threads.stop(self._thread)
