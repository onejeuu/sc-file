from PySide6.QtCore import QMutex, QMutexLocker, QObject, QThread, Signal, Slot


class RequestTokens:
    def __init__(self) -> None:
        self._mutex = QMutex()
        self._latest = 0

    def next(self) -> int:
        with QMutexLocker(self._mutex):
            self._latest += 1
            return self._latest

    def matches(self, token: int) -> bool:
        with QMutexLocker(self._mutex):
            return token == self._latest


class JobWorker(QObject):
    finished = Signal()

    @Slot()
    def run(self) -> None:
        try:
            self._run()

        finally:
            self.finished.emit()

    def _run(self) -> None:
        raise NotImplementedError


def worker(parent: QObject, worker: QObject) -> QThread:
    thread = QThread(parent)
    worker.moveToThread(thread)
    thread.finished.connect(worker.deleteLater)
    return thread


def job(
    parent: QObject,
    worker: JobWorker,
) -> QThread:
    thread = QThread(parent)
    worker.moveToThread(thread)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.started.connect(worker.run)
    return thread


def stop(thread: QThread) -> None:
    if thread.isRunning():
        thread.quit()
        thread.wait()
