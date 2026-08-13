from collections.abc import Callable

from PySide6.QtCore import QMutex, QMutexLocker, QObject, QThread, SignalInstance


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


def worker(parent: QObject, worker: QObject) -> QThread:
    thread = QThread(parent)
    worker.moveToThread(thread)
    thread.finished.connect(worker.deleteLater)
    return thread


def job(
    parent: QObject,
    worker: QObject,
    run: Callable[[], None],
    finished: SignalInstance,
    done: Callable[[], None],
) -> QThread:
    thread = QThread(parent)
    worker.moveToThread(thread)
    finished.connect(thread.quit)
    finished.connect(worker.deleteLater)
    thread.finished.connect(done)
    thread.finished.connect(thread.deleteLater)
    thread.started.connect(run)
    return thread


def stop(thread: QThread) -> None:
    if thread.isRunning():
        thread.quit()
        thread.wait()
