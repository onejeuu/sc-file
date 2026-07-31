from abc import ABCMeta, abstractmethod
from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Signal


_THREADS: dict[QThread, "Worker"] = {}


class WorkerMeta(ABCMeta, type(QObject)): ...


class Worker(QObject, metaclass=WorkerMeta):
    finished = Signal()

    @abstractmethod
    def run(self) -> None: ...

    def stop(self) -> None:
        """Request worker-specific cancellation."""


def execute(
    worker: Worker,
    on_done: Callable[[], None] | None = None,
) -> QThread:
    thread = QThread()
    worker.moveToThread(thread)

    if on_done:
        thread.finished.connect(on_done)

    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    _THREADS[thread] = worker
    thread.finished.connect(lambda: _THREADS.pop(thread, None))
    thread.finished.connect(thread.deleteLater)

    thread.started.connect(worker.run)
    thread.start()
    return thread


def stop(
    worker: Worker,
    thread: QThread,
) -> None:
    """Request cancellation and wait for thread to finish."""

    if not thread.isRunning():
        return

    worker.stop()
    thread.requestInterruption()
    thread.quit()
    thread.wait()


def stop_all() -> None:
    """Stop all active workers."""

    for thread, worker in tuple(_THREADS.items()):
        stop(worker, thread)
