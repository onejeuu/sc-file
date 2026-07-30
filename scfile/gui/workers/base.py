from abc import ABCMeta, abstractmethod

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
    on_done=None,
) -> QThread:
    thread = QThread()
    worker.moveToThread(thread)

    if on_done:
        thread.finished.connect(on_done)

    worker.finished.connect(thread.quit)
    _THREADS[thread] = worker
    thread.finished.connect(lambda: _THREADS.pop(thread, None))

    thread.started.connect(worker.run)
    thread.start()
    return thread


def stop(
    worker: Worker,
    thread: QThread,
) -> None:
    """Request cancellation and wait for thread to finish."""

    worker.stop()
    thread.requestInterruption()
    thread.quit()
    thread.wait()
