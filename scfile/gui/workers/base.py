from abc import ABCMeta, abstractmethod

from PySide6.QtCore import QObject, QThread, Signal


class WorkerMeta(ABCMeta, type(QObject)):
    pass


class Worker(QObject, metaclass=WorkerMeta):
    finished = Signal()

    @abstractmethod
    def run(self) -> None:
        pass


def execute(worker: Worker, on_done=None) -> QThread:
    thread = QThread()
    worker.moveToThread(thread)

    if on_done:
        worker.finished.connect(on_done)

    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.started.connect(worker.run)
    thread.start()
    return thread
