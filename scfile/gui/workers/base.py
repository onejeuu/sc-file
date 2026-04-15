from abc import ABCMeta, abstractmethod

from PySide6.QtCore import QObject, QThread, Signal


class WorkerMeta(ABCMeta, type(QObject)):
    pass


class Worker(QObject, metaclass=WorkerMeta):
    finished = Signal()
    error = Signal(str)

    @abstractmethod
    def run(self) -> None:
        pass


def execute(worker: Worker, on_done=None, on_error=None) -> QThread:
    thread = QThread()
    worker.moveToThread(thread)

    if on_done:
        worker.finished.connect(on_done)

    if on_error:
        worker.error.connect(on_error)

    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.started.connect(worker.run)
    thread.start()
    return thread
